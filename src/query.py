import json
from nltk.stem import PorterStemmer
from src.helpers import tokenize

class QueryException(Exception):
    pass

IndexData = list[dict[str: int]]

def get(filename: str) -> dict[str: IndexData]:
    try:
        with open(filename, "r") as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        return {}

def merge(data1: set[int], data2: set[int]) -> set[int]:
    return data1.intersection(data2)

def toIdList(data: IndexData) -> set[int]:
    s = set()
    for d in data:
        s.add(d["id"])
    return s

def searchIndex(query: str, indexLoc: str) -> list[str]:
    """Query an index.

    Args:
        query (str): the query to search for.
        indexLoc (str): the location of the index to query.

    Returns:
        list[str]: a list of document names that matched the query.
    """
    try:
        with open(f"{indexLoc}/meta.json", "r") as f:
            meta = json.load(f)
        filename: str = meta["filename"]
        breakpoints: list[str] = meta["breakpoints"]
    except FileNotFoundError:
        raise QueryException(f"Index metadata file not found at: {indexLoc}")
    except KeyError:
        raise QueryException(f"Malformed metadata file at: {indexLoc}")
    
    stemmer = PorterStemmer()
    resultDocs: dict[str: IndexData] = {}
    brks = iter(breakpoints + [None])
    
    terms = [stemmer.stem(w) for w in tokenize(query)]
    terms.sort()
    
    id = 0
    data = get(f"{indexLoc}/{filename}{id}.json")
    brk = next(brks)
    for term in terms:
        try:
            if brk is not None and term >= brk:
                while brk is not None and term >= brk:
                    id += 1
                    brk = next(brks)
                data = get(f"{indexLoc}/{filename}{id}.json")
            resultDocs[term] = data[term]
        except KeyError:
            continue
    
    results = iter(sorted(resultDocs.values(), key = lambda x: len(x)))
    try:
        out: set[int] = toIdList(next(results))
    except StopIteration:
        return []
    for r in results:
        out = merge(out, toIdList(r))
    return out