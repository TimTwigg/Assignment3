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
        if len(self._cache_) > self.CACHE_SIZE:
            self._cache_[self.pointer] = {term: results}
            self.pointer = (self.pointer + 1) % self.CACHE_SIZE
        else:
            self._cache_.append({term: results})
    
    def _check_cache_(self, term: str) -> None|list[str]:
        for r in self._cache_:
            if term in r:
                return r[term]
        return None

    def get(self, filename: str) -> dict[str: IndexData]:
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
        return data1.intersection(data2)

    def toIdList(self, data: IndexData) -> set[int]:
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
        
        terms = [self.stemmer.stem(w) for w in tokenize(query)]
        terms.sort()
        
        id = -1
        data = {}
        brk = next(brks)
        for term in terms:
            cacheResult = self._check_cache_(term)
            if cacheResult is not None:
                resultDocs[term] = cacheResult
                continue
            try:
                if brk is not None and term >= brk:
                    while brk is not None and term >= brk:
                        id += 1
                        brk = next(brks)
                    data = self.get(f"{self.indexLoc}/{self.filename}{id}.json")
                resultDocs[term] = data[term]
                self._add_cache_(term, data[term])
            except KeyError:
                continue
        
        results = iter(sorted(resultDocs.values(), key = lambda x: len(x)))
        try:
            out: set[int] = self.toIdList(next(results))
        except StopIteration:
            return []
        for r in results:
            out = self.merge(out, self.toIdList(r))
        
        # self._add_cache_(query, out)
        return out