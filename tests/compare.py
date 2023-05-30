from typing import Callable
import timeit
import random
random.seed(1234)

def timeList(func: Callable[[None], None], tests: int = 10) -> list[float]:
    return timeit.repeat(func, number = 1000, repeat = tests)

def compare() -> None:
    length = 1000
    l = [random.randint(0, 1) for _ in range(length)]
    
    def f1():
        res = int("".join(str(i) for i in l), 2)
    
    def f2():
        res = 0
        for ele in l:
            res = (res << 1) | ele
    
    def f3():
        res = sum(x * 2**i for i, x in enumerate(reversed(l)))
    
    print(timeList(f1))
    print(timeList(f2))
    print(timeList(f3))