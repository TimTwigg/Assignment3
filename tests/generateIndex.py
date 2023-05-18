import random
from src.matrix import Matrix, Posting

def generateMatrix(folder: str) -> None:
    literals = "0123456789abcdefghijklmnopqrstuvwxyz"
    data = {l: Posting(id, random.randint(0, 1000)) for id,l in enumerate(literals)}
    matrix = Matrix(folder = folder, clean = True)
    for k,v in data.items():
        matrix.add(k, v, k)
    matrix.save()