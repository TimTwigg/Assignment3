import cProfile

def analyse() -> None:
    cProfile.run("searchIndex('acm', 'indexLarge')")