from src.refactor import refactor
from tests.analyse import analyse
from src.query import searchIndex

breakpoints = sorted([*"0123456789abcdefghijklmnopqrstuvwxyz", *[f"{l}m" for l in "abcdefghijklmnopqrstuvwxyz"]])

def main():
    refactor("indexLarge", "matrix", breakpoints, True, True)
    # analyse()

if __name__ == "__main__":
    main()