import json
from pathlib import Path

class RefactorException(Exception):
    pass

def refactor(indexPath: str, rfName: str, breakpoints: list[str], printing: bool = True, clean: bool = False) -> None:
    """Refactor an index to a new set of breakpoints.

    Args:
        indexPath (str): the location of the index folder.
        rfName (str): the name of the refactored index files. Must be different from the original index file names.
        breakpoints (list[str]): the new set of breakpoints.
        printing (bool, optional): whether to print progress markers. Defaults to True.
        clean (bool, optional): whether to delete the old index. Defaults to False.
    """
        
    try:
        with open(f"{indexPath}/meta.json", "r") as f:
            meta = json.load(f)
        filename = meta["filename"]
    except FileNotFoundError:
        raise RefactorException(f"Index metadata file not found at: {indexPath}")
    except KeyError:
        raise RefactorException(f"Malformed metadata: {filename}/meta.json")
    
    if filename == rfName:
        raise RefactorException(f"New index filename cannot be the same as the original index filename.")
    
    if printing:
        print("Begin Refactoring")
        print("Breakpoints:", breakpoints)
    
    brks = iter(breakpoints + [None, None])
    brk = next(brks)
    id = 0
    outId = 0
    data: dict = {}
    out = {}
    
    # local func to save index segment to file
    def dump() -> None:
        nonlocal out, outId, brk
        if printing:
            print("Saving Index Segment:", outId)
        with open(f"{indexPath}/{rfName}{outId}.json", "w") as f:
            json.dump(out, f, indent = 4)
            out.clear()
            outId += 1
            brk = next(brks)
    
    while True:
        # for keys in current data, add to new index segment, dumping if a key is reached which is in the subsequent segment
        for k in sorted(data.keys()):
            if brk is None or k < brk:
                out[k] = data.pop(k)
            else:
                dump()
                break
        
        # get the next index file
        if len(data) < 1:
            try:
                with open(f"{indexPath}/{filename}{id}.json", "r") as f:
                    data.update(json.load(f))
                    id += 1
            except FileNotFoundError:
                break
    
    dump()
    
    # save metadata
    with open(f"{indexPath}/{'meta' if clean else rfName + 'meta'}.json", "w") as f:
        meta = {
            "filename": rfName,
            "breakpoints": breakpoints
        }
        json.dump(meta, f, indent = 4)
    
    # delete old index files
    if clean:
        if printing:
            print("Cleaning Old Index")
        id = 0
        path = Path(f"{indexPath}/{filename}{id}.json")
        while path.exists():
            path.unlink()
            id += 1
            path = Path(f"{indexPath}/{filename}{id}.json")
    
    if printing:
        print("Refactoring Complete")