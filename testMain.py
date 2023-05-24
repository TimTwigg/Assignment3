# import cProfile
# from src.query import Queryier
from tests.test_matrix import test_matrix

# def test():
#     q = Queryier("indexLarge")
#     q.searchIndex("master of software engineering")
#     q.searchIndex("engineering")

def main():
    # cProfile.run("test()")
    test_matrix()

if __name__ == "__main__":
    main()