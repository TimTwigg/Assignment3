from src.indexer import Indexer, Site
from src.matrix import  Matrix, Posting
import os

def CreateIndex(dataset: str = "test"):
    print("Index Dataset:", dataset)
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
        if count % 100 == 0:
            print(f"Indexed {count} pages. Found {matrix.size()} distinct tokens.")
    
    matrix.save()
    
    size = os.stat("matrix.json").st_size
    with open("summary.txt", "w") as f:
        f.write(
f"""Number of pages: {count}
Number of unique tokens: {matrix.size()}
Filesize: {size / 1024:.4f} kb | {size / 1024**2:.4f} mb | {size / 1024**3:.4f} gb
""")

    print("Indexing Complete")

if __name__ == "__main__":
    CreateIndex()
    