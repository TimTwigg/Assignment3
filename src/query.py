from msgspec.json import decode
from nltk.stem import SnowballStemmer
from typing import TextIO
import csv
from src.helpers import tokenize
from src.config import Config

class QueryException(Exception):
    pass

IndexData = list[dict[str: int]]

class Queryier:    
    def __init__(self, indexLoc: str, cache_size: int = 25):
        """Create Queryier object to query an index.

        Args:
            indexLoc (str): the folder containing the index.
            cache_size (int, optional): how many query terms to store in the cache. Defaults to 25.

        Raises:
            QueryException: if the index is not found or if the index metadata file is missing/malformed.
        """
        # read meta data
        try:
            with open(f"{indexLoc}/meta.json", "r") as f:
                meta = decode(f.read())
            self.filename: str = meta["filename"]
            self.breakpoints: list[str] = meta["breakpoints"]
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
        self._cache_: list[dict[str:list[str]]] = []
        self.stemmer = SnowballStemmer("english")
        self.docs = self.getDocs()
        self._files_: list[TextIO] = [open(f"{indexLoc}/{self.filename}{i}.csv", "r") for i in range(len(self.breakpoints)+1)]
        self.config = Config()
        
        # load stopwords
        try:
            with open("stop_words.txt", "r") as f:
                self.stopwords = set(self.stemmer.stem(s) for s in f.readlines())
        except FileNotFoundError:
            raise QueryException("Stopwords file not found")
    
    def __del__(self):
        """Destructor. Closes all index files."""
        for f in self._files_:
            f.close()
    
    def _add_cache_(self, term: str, results: list[str]) -> None:
        """Add a term and its index results to the cache, replacing the oldest cache entry if the cache is full.

        Args:
            term (str): the term to add.
            results (list[str]): the documents returned as results for that term.
        """
        if len(self._cache_) > self.CACHE_SIZE:
            self._cache_[self.pointer] = {term: results}
            self.pointer = (self.pointer + 1) % self.CACHE_SIZE
        else:
            self._cache_.append({term: results})
    
    def _check_cache_(self, term: str) -> None|list[str]:
        """Check if a term is in the cache.

        Args:
            term (str): the term to search for.

        Returns:
            None|list[str]: the list of results stored in the cache. Returns None if the term was not in the cache.
        """
        for r in self._cache_:
            if term in r:
                return r[term]
        return None
    
    def getToken(self, token: str) -> list[dict[str:int]]:
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
        # return the decoded items in the line
        return [decode(d) for row in reader for d in row if d != token]
    
    def getDocs(self) -> dict[int: str]:
        """Load the documents dict"""
        docs = {}
        with open(f"{self.indexLoc}/documents.csv", "r") as f:
            reader = csv.reader(f)
            for row in reader:
                docs[int(row[0])] = row[1]
        return docs
    
    def rankSort(self, results: list[dict[str:int]]) -> None:
        """Inplace sort the results for a token

        Args:
            results (list[dict[str:int]]): the results to sort.
        """
        results.sort(key = lambda x: x["frequency"], reverse = True)

    def searchIndex(self, query: str, useStopWords: bool = False) -> list[str]:
        """Query an index.

        Args:
            query (str): the query to search for.
            useStopWords (str, optional): whether to include stopwords in the searched-for terms. Defaults to False.

        Returns:
            list[str]: a list of document names that matched the query.
        """
        
        resultDocs: dict[str: IndexData] = {}
        
        # stem query tokens
        terms = [self.stemmer.stem(w) for w in tokenize(query)]
        if useStopWords:
            terms = [w for w in terms if w not in self.stopwords]
        # for each token in the query
        for term in terms:
            # check cache
            cacheResult = self._check_cache_(term)
            if cacheResult is not None:
                resultDocs[term] = cacheResult
                continue
            try:
                results = self.getToken(term)
                # sort the results by rank
                self.rankSort(results)
                # add the postings for the term to the results
                resultDocs[term] = results
                # add to cache
                self._add_cache_(term, results)
            except KeyError:
                # if the term is not found in the index
                # currently ignores this failure
                continue
        
        ###################################################################
        # TODO rewrite this section to use ranked retrieval
        
        # sort results by increasing size
        results = iter(sorted(resultDocs.values(), key = lambda x: len(x)))
        try:
            out: set[int] = set(d["id"] for d in next(results))
        except StopIteration:
            # return empty list if no results were found
            return []
        # merge results starting with smallest result for faster merging
        for r in results:
            out = out.intersection(set(d["id"] for d in r))
        
        # change ids to urls
        urls: list[str] = []
        for id in out:
            urls.append(self.docs[id])
        
        ###################################################################
        
        if len(urls) < self.config.k_results and not useStopWords:
            return self.searchIndex(query, True)
        
        return urls