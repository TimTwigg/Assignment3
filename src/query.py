import json
from msgspec.json import decode
from nltk.stem import SnowballStemmer
import time
from src.helpers import tokenize

class QueryException(Exception):
    pass

IndexData = list[dict[str: int]]

class Queryier:    
    def __init__(self, indexLoc: str, cache_size: int = 10):
        """Create Queryier object to query an index.

        Args:
            indexLoc (str): the folder containing the index.
            cache_size (int, optional): how many query terms to store in the cache. Defaults to 10.

        Raises:
            QueryException: if the index is not found or if the index metadata file is missing/malformed.
        """
        self.CACHE_SIZE = cache_size
        self._cache_: list[dict[str:list[str]]] = []
        self.pointer = 0
        self.indexLoc = indexLoc
        
        try:
            with open(f"{indexLoc}/meta.json", "r") as f:
                meta = json.load(f)
            self.filename: str = meta["filename"]
            self.breakpoints: list[str] = meta["breakpoints"]
        except FileNotFoundError:
            raise QueryException(f"Index metadata file not found at: {indexLoc}")
        except KeyError:
            raise QueryException(f"Malformed metadata file at: {indexLoc}")
        
        self.stemmer = SnowballStemmer("english")
    
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

    def get(self, filename: str) -> dict[str: IndexData]:
        """Load the data from an index file.
        
        Args:
            filename (str): the filename to open.

        Returns:
            dict[str: IndexData]: the submatrix loaded from the file. Returns an empty dict if the file was not found.
        """
        try:
            start = time.process_time_ns()
            with open(filename, "r") as f:
                data = decode(f.read())
            end = time.process_time_ns()
            print("Get:", (end-start) / 10**6, "ms")
            return data
        except FileNotFoundError:
            return {}

    def merge(self, data1: set[int], data2: set[int]) -> set[int]:
        """Merge two sets together, leaving both untouched."""
        return data1.intersection(data2)

    def toIdList(self, data: IndexData) -> set[int]:
        """Extract ids from IndexData"""
        s = set()
        for d in data:
            s.add(d["id"])
        return s

    def searchIndex(self, query: str) -> list[str]:
        """Query an index.

        Args:
            query (str): the query to search for.
            indexLoc (str): the location of the index to query.

        Returns:
            list[str]: a list of document names that matched the query.
        """
        
        resultDocs: dict[str: IndexData] = {}
        brks = iter(["/"] + self.breakpoints + [None])
        
        # stem query tokens
        terms = [self.stemmer.stem(w) for w in tokenize(query)]
        # sort to streamline index retrieval
        terms.sort()
        
        id = -1
        data = {}
        brk = next(brks)
        # for each token in the query
        for term in terms:
            # check cache
            cacheResult = self._check_cache_(term)
            if cacheResult is not None:
                resultDocs[term] = cacheResult
                continue
            try:
                # skip through to the correct index file and load it
                if brk is not None and term >= brk:
                    while brk is not None and term >= brk:
                        id += 1
                        brk = next(brks)
                    data = self.get(f"{self.indexLoc}/{self.filename}{id}.json")
                # add the postings for the term to the results
                resultDocs[term] = data[term]
                # add to cache
                self._add_cache_(term, data[term])
            except KeyError:
                # if the term is not found in the index
                # currently ignores this failure
                continue
        
        # sort results by increasing size
        results = iter(sorted(resultDocs.values(), key = lambda x: len(x)))
        try:
            out: set[int] = self.toIdList(next(results))
        except StopIteration:
            # return empty list if no results were found
            return []
        # merge results starting with smallest result for faster merging
        for r in results:
            out = self.merge(out, self.toIdList(r))
        
        return out