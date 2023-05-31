from typing import Callable
import timeit
import random
import numpy as np

def timeList(func: Callable[[None], None], tests: int = 10) -> list[float]:
    return timeit.repeat(func, number = 1, repeat = tests)

def compare() -> None:
        
    def f1():
        pass
    
    def f2():
        pass
    
    t1 = timeList(f1)
    t2 = timeList(f2)
    
    res = np.sum(np.subtract(t1, t2))
    print("Result:", "f1" if res < 0 else "f2", "by", abs(res), "seconds.")
    