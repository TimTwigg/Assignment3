from typing import Callable
import time
import json
from main import CreateIndex

def timeit(func: Callable[[None], None]) -> float:
    start = time.process_time_ns()
    func()
    end = time.process_time_ns()
    return end - start

def timeList(func: Callable[[None], None], tests: int = 1) -> list[float]:
    return [timeit(func) for _ in range(tests)]

def compare() -> None:
    # test breakpoints
    f = lambda brk: CreateIndex(chunkSize = 500, offload = False, printing = True, maxDocs = 2500, breakpoints = brk)
    times = []
    for brk in [["a", "i", "r"], ["a", "g", "m", "t"], ["5", "a", "f", "k", "p", "u"]]:
        times.append(timeList(lambda: f(brk)))
        print()
    
    for tl in times:
        print(tl)
    
    with open("results.json", "w") as f:
        json.dump(times, f, indent = 4)