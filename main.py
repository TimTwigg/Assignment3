from src import Indexer, Site, Matrix, Posting
import os

def CreateIndex():
    indexer = Indexer()
    matrix: Matrix = Matrix()
    count = 0
    tokens: Site = indexer.getNextSite()
    while tokens:
        for k,v in tokens.tokens.items():
            matrix.add(k, Posting(hash(tokens.path.name), v))
        tokens = indexer.getNextSite()
        count += 1
        if count % 500 == 0:
            print(f"Indexed {count} pages")
        if count > 100:
            break
    
    matrix.save()
    
    size = os.stat("matrix.json").st_size
    with open("summary.txt", "w") as f:
        f.write(
f"""Number of pages: {count}
Number of unique tokens: {matrix.size()}
Filesize: {size / 1024:.4f} kb | {size / 1024**2:.4f} mb | {size / 1024**3:.4f} gb
""")

    print("Complete")

if __name__ == "__main__":
    CreateIndex()
    