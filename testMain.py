import cProfile
from src.query import Queryier

def test():
    q = Queryier("indexLarge")
    q.searchIndex("master of software engineering")
    q.searchIndex("engineering")

def main():
    cProfile.run("test()")

if __name__ == "__main__":
    main()