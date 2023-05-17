import os
import argparse
import time
from src.indexer import Indexer, Site
from src.matrix import  Matrix, Posting
from src.query import Queryier
# from src.queryC import searchIndex

def CreateIndex(dataset: str = "test", chunkSize: int = 100, offload: bool = False, printing: bool = True, maxDocs: int = None, breakpoints: list[str] = ["a", "i", "r"]):
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
    while tokens:
        for k,v in tokens.tokens.items():
            matrix.add(k, Posting(hash(tokens.path.name), v))
        tokens = indexer.getNextSite()
        count += 1
        if count % chunkSize == 0:
            if printing:
                print(f"\nIndexed {count} pages.")
            if offload:
                if printing:
                    print("Offloading Matrix: ", end = "")
                matrix.save()
                if printing:
                    print("Done")
        if maxDocs is not None and count >= maxDocs:
            break
    
    time_end = time.process_time()
    print(f"\nFinished Dataset: {count} pages.")
    matrix.save()
    
    sizes = [os.stat(f"index/matrix{i}.json").st_size for i in range(matrix._matrix_count_)]
    total = sum(sizes)
    with open("summary.txt", "w") as f:
        f.write(f"Number of pages: {count}\nNumber of unique tokens: {matrix.scan_size()}\n" +
            "\n".join(f"  Matrix {i} Filesize: {size / 1024:.4f} kb | {size / 1024**2:.4f} mb | {size / 1024**3:.4f} gb" for i,size in enumerate(sizes)) +
            f"\nTotal Index File Size: {total / 1024:.4f} kb | {total / 1024**2:.4f} mb | {total / 1024**3:.4f} gb" +
            f"\nTime to Create Index: {time_end - time_start} seconds")

    print("Time:", time_end-time_start, "seconds")
    print("\nIndexing Complete")

def queryIndex(indexFolderPath: str = "index") -> None:
    print("Search Index:", indexFolderPath)
    q = Queryier(indexFolderPath)
    while True:
        query = input("q:> ")
        if len(query.strip()) < 1:
            break
        time_start = time.process_time_ns()
        results = q.searchIndex(query)
        time_end = time.process_time_ns()
        # for r in results:
        #     print(f"    {r}")
        print(f"  Results: {len(results)}")
        print(f"  Time: {(time_end-time_start) / 10**6} ms")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = "Run Indexer and Search Engine")
    parser.add_argument("--index", help = "Run Indexer", action = argparse.BooleanOptionalAction)
    parser.add_argument("--query", help = "Run Search Engine Querier", action = argparse.BooleanOptionalAction)
    parser.add_argument("-d", "--dataset", help = "Which dataset to index, defaults to testing set. [Indexer Only]", nargs = "?", type = str, default = "test")
    parser.add_argument("-c", "--chunksize", help = "Indexing Chunk Size, defaults to 100. [Indexer Only]", nargs = "?", type = int, default = 100)
    parser.add_argument("-o", "--offload", help = "Offload chunks as they are loaded, defaults to False. [Indexer Only]", action = argparse.BooleanOptionalAction)
    parser.add_argument("-p", "--printing", help = "Don't print progress.", action = argparse.BooleanOptionalAction)
    parser.add_argument("-m", "--maxDocs", help = "Set maximum number of documents to index. Defaults to no limit. [Indexer Only]", nargs = "?", type = int, default = -1)
    parser.add_argument("-b", "--breakpoints", help = "Set breakpoints for indexer. [Indexer only]", nargs = "+", type = str, default = ["a", "i", "r"])
    parser.add_argument("-i", "--indexSource", help = "The index to search. Defaults to testing index. [Querier only]", nargs = "?", type = str, default = "indexSmall")
    args = parser.parse_args()
    
    if args.index:
        CreateIndex(args.dataset, args.chunksize, args.offload, not args.printing, None if args.maxDocs < 0 else args.maxDocs, args.breakpoints)
    elif args.query:
        queryIndex(args.indexSource)