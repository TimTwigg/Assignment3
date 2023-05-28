import os
import argparse
import time
import json
from src.indexer import Indexer, Site
from src.matrix import  Matrix, Posting
from src.query import Queryier
from src.refactor import refactor, RefactorException

def CreateIndex(dataset: str = "test", chunkSize: int = 1000, offload: bool = True, printing: bool = True, maxDocs: int = None, breakpoints: list[str] = ["a", "i", "r"]):
    """Create an index from a dataset.

    Args:
        dataset (str, optional): which dataset to index, can be "test" or "large". Defaults to "test".
        chunkSize (int, optional): the number of documents to keep in memory at a time. Defaults to 1000.
        offload (bool, optional): whether to save partial indexes during the process, merging them at the end. Defaults to True.
        printing (bool, optional): whether to print progress reports during index creation. Defaults to True.
        maxDocs (int, optional): the limit on how many documents to index. Defaults to None.
        breakpoints (list[str], optional): the breakpoints to divide the tokens by. Defaults to ["a", "i", "r"].
    """
    
    if len(breakpoints) == 1 and breakpoints[0].lower() == "none":
        breakpoints = []
    
    time_start = time.process_time()
    if printing:
        print("Index Dataset:", dataset)
        print("Chunk Size:", chunkSize)
        print("Offload:", "Yes" if offload else "No")
        print("Limit Document Count:", f"Yes ({maxDocs})" if maxDocs is not None else "No")
        print("Breakpoints:", breakpoints)
        print("Creating Index: ", end = "")
    indexer = Indexer(dataset)
    if printing:
        print("Done")
        print("Creating Matrix: ", end = "")
    matrix: Matrix = Matrix(breakpoints = breakpoints, clean = True)
    if printing:
        print("Done")
        print("Begin Indexing")
    
    count = 0
    tokens: Site = indexer.getNextSite()
    # while there's another document to index
    while tokens:
        # insert each token to the matrix
        for k,v in tokens.tokens.items():
            matrix.add(k, Posting(hash(tokens.url), v, k in tokens.headers, k in tokens.bold, k in tokens.titles), tokens.url)
        tokens = indexer.getNextSite()
        count += 1
        # print progress and offload every chunkSize documents
        if count % chunkSize == 0:
            if printing:
                print(f"\nIndexed {count} pages.")
            if offload:
                if printing:
                    print("Offloading Matrix: ", end = "")
                matrix.save()
                if printing:
                    print("Done")
        # break if maxDocs documents have been indexed
        if maxDocs is not None and count >= maxDocs:
            break
    
    matrix.save()
    if printing:
        print(f"\nFinished Dataset: {count} pages.")
        print("Consolidating Index: ", end = "")
    matrix.finalize(printing)
    if printing:
        print("Done")
    time_end = time.process_time()
    
    # save summary stats
    sizes = [os.stat(f"index/matrix{i}.csv").st_size for i in range(matrix._matrix_count_)]
    total = sum(sizes)
    with open("summary.txt", "w") as f:
        f.write(f"Number of pages: {count}\nNumber of unique tokens: {matrix.scan_size()}\n" +
            "\n".join(f"  Matrix {i} Filesize: {size / 1024:.4f} kb | {size / 1024**2:.4f} mb | {size / 1024**3:.4f} gb" for i,size in enumerate(sizes)) +
            f"\nTotal Index File Size: {total / 1024:.4f} kb | {total / 1024**2:.4f} mb | {total / 1024**3:.4f} gb" +
            f"\nTime to Create Index: {time_end-time_start:.2f} seconds | {(time_end-time_start)/60:.2f} minutes")

    print("Time:", time_end-time_start, "seconds")
    print("\nIndexing Complete")

def queryIndex(indexFolderPath: str = "index") -> None:
    """Query an index.

    Args:
        indexFolderPath (str, optional): the folder containing the index to query. Defaults to "index".
        printNum (int, optional): the number of results to print. Defaults to 0.
    """
    print("Search Index:", indexFolderPath)
    print("Enter query to search. To exit, press enter on a blank query.")
    q = Queryier(indexFolderPath)
    while True:
        query = input("\nq:> ")
        if len(query.strip()) < 1:
            break
        time_start = time.process_time_ns()
        results = q.searchIndex(query)
        time_end = time.process_time_ns()
        for r in results:
            print(f"    {r}")
        print(f"  Results: {len(results)}")
        print(f"  Time: {(time_end-time_start) / 10**6} ms")

def refactorIndex(index: str, breakpoints: list[str], printing: bool):
    if len(breakpoints) == 1:
        if breakpoints[0].lower() == "long":
            breakpoints = sorted([*"0123456789abcdefghijklmnopqrstuvwxyz", *[f"{l}m" for l in "abcdefghijklmnopqrstuvwxyz"]])
        elif breakpoints[0].lower() == "mid":
            breakpoints = [*"0123456789abcdefghijklmnopqrstuvwxyz"]
        elif breakpoints[0].lower() == "short":
            breakpoints = [*"048cgkosw"]
        elif breakpoints[0].lower() == "none":
            breakpoints = []
    filename = "matrix"
    try:
        refactor(index, filename, breakpoints, printing, True)
    except RefactorException:
        filename = "index"
        refactor(index, filename, breakpoints, printing, True)

    # resave the meta
    with open(f"{index}/meta.json", "r") as f:
        meta = json.load(f)
    meta["filename"] = filename
    meta["breakpoints"] = breakpoints
    with open(f"{index}/meta.json", "w") as f:
        json.dump(meta, f, indent = 4)
    
    # reform the meta index
    matrix = Matrix(folder = index, breakpoints = breakpoints, filename = filename)
    matrix._matrix_count_ = len(breakpoints)+1
    meta_index = matrix._index_matrix_()
    with open(f"{index}/meta_index.json", "w") as f:
        json.dump(meta_index, f, indent = 4)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = "Run Indexer and Search Engine")
    parser.add_argument("--index", help = "Run Indexer", action = argparse.BooleanOptionalAction)
    parser.add_argument("--query", help = "Run Search Engine Querier", action = argparse.BooleanOptionalAction)
    parser.add_argument("--refactor", help = "Refactor an Index", action = argparse.BooleanOptionalAction)
    parser.add_argument("-d", "--dataset", help = "Which dataset to index, defaults to testing set. [Indexer Only]", nargs = "?", type = str, default = "test")
    parser.add_argument("-c", "--chunksize", help = "Indexing Chunk Size, defaults to 1000. [Indexer Only]", nargs = "?", type = int, default = 1000)
    parser.add_argument("-o", "--offload", help = "Offload chunks as they are loaded, defaults to False. [Indexer Only]", action = argparse.BooleanOptionalAction)
    parser.add_argument("-p", "--printing", help = "Print progress.", action = argparse.BooleanOptionalAction)
    parser.add_argument("-m", "--maxDocs", help = "Set maximum number of documents to index. Defaults to None. [Indexer only]", nargs = "?", type = int, default = -1)
    parser.add_argument("-b", "--breakpoints", help = "Set breakpoints for indexer. [Indexer or Refactoring]", nargs = "+", type = str, default = ["a", "i", "r"])
    parser.add_argument("-i", "--indexSource", help = "The index to search. Defaults to testing index. [Querier or Refactoring]", nargs = "?", type = str, default = "indexSmall")
    args = parser.parse_args()
    
    if args.index:
        CreateIndex(args.dataset, args.chunksize, args.offload, args.printing, None if args.maxDocs < 0 else args.maxDocs, args.breakpoints)
    elif args.query:
        queryIndex(args.indexSource)
    elif args.refactor:
        refactorIndex(args.indexSource, args.breakpoints, args.printing)