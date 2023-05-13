import os
import argparse
from src.indexer import Indexer, Site
from src.matrix import  Matrix, Posting

def CreateIndex(dataset: str = "test", chunkSize: int = 100, offload: bool = False):
    print("Index Dataset:", dataset)
    print("Chunk Size:", chunkSize)
    print("Offload:", "Yes" if offload else "No")
    print("Creating Index: ", end = "")
    indexer = Indexer(dataset)
    print("Done")
    print("Creating Matrix: ", end = "")
    matrix: Matrix = Matrix()
    print("Done")
    count = 0
    print("Begin Indexing")
    tokens: Site = indexer.getNextSite()
    while tokens:
        for k,v in tokens.tokens.items():
            matrix.add(k, Posting(str(hash(tokens.path.name)), v))
        tokens = indexer.getNextSite()
        count += 1
        if count % chunkSize == 0:
            print(f"\nIndexed {count} pages.")
            if offload:
                print("Offloading Matrix: ", end = "")
                matrix.save()
                print("Done")
    
    matrix.save()
    
    sizes = [os.stat(f"matrix{i}.json").st_size for i in range(1, 5)]
    total = sum(sizes)
    with open("summary.txt", "w") as f:
        f.write(f"Number of pages: {count}\nNumber of unique tokens: {matrix.scan_size()}\n" +
            "\n".join(f"Matrix {i} Filesize: {size / 1024:.4f} kb | {size / 1024**2:.4f} mb | {size / 1024**3:.4f} gb" for i,size in enumerate(sizes, start = 1)) +
            f"\nTotal Index File Size: {total / 1024:.4f} kb | {total / 1024**2:.4f} mb | {total / 1024**3:.4f} gb")

    print("Indexing Complete")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = "Run Search Engine")
    parser.add_argument("-d", "--dataset", help = "Which dataset to index, defaults to testing set.", nargs = "?", type = str, default = "test")
    parser.add_argument("-c", "--chunksize", help = "Indexing Chunk Size, defaults to 100.", nargs = "?", type = int, default = 100)
    parser.add_argument("-o", "--offload", help = "Offload chunks as they are loaded, defaults to False.", action = argparse.BooleanOptionalAction)
    args = parser.parse_args()
    
    CreateIndex(args.dataset, args.chunksize, args.offload)
    