from src.refactor import refactor

def main():
    refactor("indexSmall", "matrix", [*"123456789abcdefghijklmnopqrstuvwxyz"], True, True)

if __name__ == "__main__":
    main()