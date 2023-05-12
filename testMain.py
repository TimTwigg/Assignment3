from tests.test_matrix import test_matrix
import time

def main():
    start = time.time()
    test_matrix()
    end = time.time()
    print(f"Time Taken: {(end - start) * 10**3}")

if __name__ == "__main__":
    main()