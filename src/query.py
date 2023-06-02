from msgspec.json import decode
from nltk.stem import SnowballStemmer
from typing import TextIO
import csv
import math
import numpy as np
from enum import Enum
from dataclasses import dataclass
from src.helpers import tokenize, multiSetIntersection
from src.config import Config

class QueryException(Exception):
    pass

class CacheStrategy(Enum):
    # replace oldest cache value
    TIMELY = 0
    # replace least popular cache value
    POPULARITY = 1

@dataclass
class Result:
    url: str
    title: str
    summary: str

IndexData = list[dict[str: int]]

class Queryier:    
    def __init__(self, indexLoc: str, cache_size: int = 25, cacheStrategy: CacheStrategy = CacheStrategy.TIMELY):
        """Create Queryier object to query an index.

        Args:
            indexLoc (str): the folder containing the index.
            cache_size (int, optional): how many query terms to store in the cache. Defaults to 25.
            cacheStrategy (CacheStrategy, optional): cache update policy. Defaults to TIMELY (overwrite oldest value).

        Raises:
            QueryException: if the index is not found or if the index metadata file is missing/malformed.
        """
        # read meta data
        try:
            with open(f"{indexLoc}/meta.json", "r") as f:
                meta = decode(f.read())
            self.filename: str = meta["filename"]
            self.breakpoints: list[str] = meta["breakpoints"]
            self.documentCount: int = meta["documentCount"]
        except FileNotFoundError:
            raise QueryException(f"Index metadata file not found at: {indexLoc}")
        except KeyError:
            raise QueryException(f"Malformed metadata file at: {indexLoc}")
        
        # read meta index
        try:
            with open(f"{indexLoc}/meta_index.json", "r") as f:
                self._meta_index_ = decode(f.read())
        except FileNotFoundError:
            raise QueryException(f"Index meta_index file not found at: {indexLoc}")
        
        self.indexLoc = indexLoc
        self.pointer = 0
        self.CACHE_SIZE = cache_size
        self.cacheStrat = cacheStrategy
        self.cacheUse: dict[int: int] = {}
        self._cache_: list[dict[str:list[str]]] = []
        self.stemmer = SnowballStemmer("english")
        self.docs = self.getDocs()
        self._files_: list[TextIO] = [open(f"{indexLoc}/{self.filename}{i}.csv", "r", encoding = "utf-8") for i in range(len(self.breakpoints)+1)]
        self.config = Config()
        
        # load stopwords
        try:
            with open("stop_words.txt", "r") as f:
                self.stopwords = set(self.stemmer.stem(s) for s in f.readlines())
        except FileNotFoundError:
            raise QueryException("Stopwords file not found")
    
    def __del__(self):
        """Destructor. Closes all index files."""
        try:
            for f in self._files_:
                f.close()
        except AttributeError:
            # occurs when an error is thrown in the constructor before the _files_ attribute is created
            # caught to prevent the destructor from throwing errors
            pass
    
    def _add_cache_(self, term: str, results: list[str]) -> None:
        """Add a term and its index results to the cache, replacing the oldest cache entry if the cache is full.

        Args:
            term (str): the term to add.
            results (list[str]): the documents returned as results for that term.
        """
        if self.CACHE_SIZE == 0:
            return None
        
        if len(self._cache_) >= self.CACHE_SIZE:
            if self.cacheStrat == CacheStrategy.TIMELY:
                self._cache_[self.pointer] = {term: results}
                self.pointer = (self.pointer + 1) % self.CACHE_SIZE
            elif self.cacheStrat == CacheStrategy.POPULARITY:
                index = min(self.cacheUse.items(), key = lambda x: x[1])[0]
                self._cache_[index] = {term: results}
                self.cacheUse[index] = 1
        else:
            self._cache_.append({term: results, "df": len(results)})
            self.cacheUse[len(self.cacheUse)] = 1
    
    def _check_cache_(self, term: str) -> None|tuple[int, list[str]]:
        """Check if a term is in the cache.

        Args:
            term (str): the term to search for.

        Returns:
            None|list[str]: the list of results stored in the cache. Returns None if the term was not in the cache.
        """
        for i,r in enumerate(self._cache_):
            if term in r:
                if self.cacheStrat == CacheStrategy.POPULARITY:
                    self.cacheUse[i] += 1
                return r["df"], r[term]
        return None
    
    def getToken(self, token: str) -> tuple[int, list[dict[str:int]]]:
        """Get the postings list for the token.

        Args:
            token (str): the token to search.

        Returns:
            list[dict[str:int]]: the postings for that token.
        """
        # position in file and file number of token
        pos, fileno = self._meta_index_[token]
        # the file containing the token
        f: TextIO = self._files_[fileno]
        # set the file pointer position
        f.seek(pos)
        # read that line
        line = f.readline()
        reader = csv.reader([line])
        line = next(reader)
        # return the decoded first r items in the line
        if self.config.r_docs > 0:
            return int(line[1]), [decode(line[i]) for i in range(2, min(self.config.r_docs, len(line)))]
        else:
            return int(line[1]), [decode(line[i]) for i in range(2, len(line))]
    
    def getDocs(self) -> dict[int: tuple[str, float]]:
        """Load the documents dict"""
        docs = {}
        with open(f"{self.indexLoc}/documents.csv", "r", encoding = "utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                docs[int(row[0])] = (row[1], float(row[2]), row[3], row[4])
        return docs

    def searchIndex(self, query: str, useStopWords: bool = False) -> tuple[list[Result], int]:
        """Query an index.

        Args:
            query (str): the query to search for.
            useStopWords (str, optional): whether to include stopwords in the searched-for terms. Defaults to False.

        Returns:
            tuple[list[str], int]: a list of document names that matched the query and the number of total results found.
        """
        
        results: dict[str: list[dict[str: int]]] = {}
        cosineSimScores: list[float] = []
        headerScores: list[float] = []
        titleScores: list[float] = []
        strongScores: list[float] = []
        conjunctiveScores: list[float] = []
        docIDs = {}
        queryDF: dict[str: float] = {}
        
        # stem query tokens
        terms = [self.stemmer.stem(w) for w in tokenize(query)]
        if not useStopWords:
            tempL = len(terms)
            terms = [w for w in terms if w not in self.stopwords]
            removedStopWords = len(terms) < tempL
        # for each token in the query
        for term in terms:
            # check cache
            cacheResult = self._check_cache_(term)
            if cacheResult is not None:
                queryDF[term] = cacheResult[0]
                results[term] = cacheResult[1]
                continue
            try:
                df, res = self.getToken(term)
                queryDF[term] = df
                results[term] = res
                # add to cache
                self._add_cache_(term, res)
            except KeyError:
                # if the term is not found in the index
                queryDF[term] = self.documentCount - 1
                results[term] = []
        
        # calculate all query term weights
        queryDF = {term: (1 + math.log10(terms.count(term))) * math.log10(self.documentCount / queryDF[term]) for term in terms}
        queryLength = math.sqrt(sum(v**2 for v in queryDF.values()))
        
        for term in terms:
            # calculate w-tq
            wtq = queryDF[term] / queryLength
            # add score for this term in each doc to the running sum
            for post in results[term]:
                id = post["id"]
                tf = 1 + math.log10(post["frequency"])
                if id not in docIDs:
                    docIDs[id] = len(docIDs)
                    cosineSimScores.append(0)
                    headerScores.append(0)
                    titleScores.append(0)
                    strongScores.append(0)
                    conjunctiveScores.append(0)
                cosineSimScores[docIDs[id]] += wtq * tf
                if post["header"]:
                    headerScores[docIDs[id]] += 1
                if post["title"]:
                    titleScores[docIDs[id]] += 1
                if post["bold"]:
                    strongScores[docIDs[id]] += 1
        
        # compute conjunctive processing score
        conjunctiveRes: set[int] = multiSetIntersection([set(p["id"] for p in v) for v in results.values()])
        for id in conjunctiveRes:
            conjunctiveScores[docIDs[id]] = 1
        
        # calculate final cosine similarity scores by dividing by normalized doc lengths
        for d,i in docIDs.items():
            cosineSimScores[i] /= self.docs[d][1]
        
        # weight the score methods
        cosineSimScores: np.ndarray = np.multiply(cosineSimScores, self.config.cosine_similarity_weight)
        headerScores: np.ndarray = np.multiply(headerScores, self.config.header_weight)
        titleScores: np.ndarray = np.multiply(titleScores, self.config.title_weight)
        strongScores: np.ndarray = np.multiply(strongScores, self.config.bold_weight)
        conjunctiveScores: np.ndarray = np.multiply(conjunctiveScores, self.config.conjunctive_weight)
        # combine relevance scores
        relevance_scores: np.ndarray = np.multiply(np.sum([cosineSimScores, headerScores, titleScores, strongScores, conjunctiveScores], 0), self.config.alpha)
        
        # authority scores
        authority_scores: np.ndarray = np.array([1]*len(relevance_scores))
        
        # sum different score methods
        scores: np.ndarray = np.sum([relevance_scores, authority_scores], 0)
        
        # divide by normalized document length and retrieve documents in rank order
        ranked = sorted(((d, scores[i]) for d,i in docIDs.items()), key = lambda x: x[1], reverse = True)
        
        # redo using stopwords if not enough results
        if len(ranked) < self.config.k_results and not useStopWords and removedStopWords:
            return self.searchIndex(query, True)
        
        # convert to urls
        urls = [Result(self.docs[d][0], self.docs[d][2], self.docs[d][3]) for d,_ in ranked[:self.config.k_results]]

        # return top k results
        return urls, len(ranked)