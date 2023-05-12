# Search Engine
CS 121/INF 141 Assignment3.

## 3rd Party Libraries
`pip install Cython` \
`pip install sortedcontainers`

## Cython Notes
Write cython files as .pyx files in the cythonLib directory. Run `compile.bat` to compile the cython to c code. The cython functions can be imported using "`from cythonLib.example import func`".

[Cython Help](https://cython.readthedocs.io/en/latest/src/userguide/language_basics.html)

## Tasks
### Milestone 1

1. write Matrix [`done`]
    - update save/load methods to work with a segmented matrix (see task 2)
        - add chunk size to Matrix
2. write cython module to search datasets and add pages to the matrix
    - must not hold entire index in memory (segmented matrix)
        - split into 3 or 4 sets of tokens alphabetically
        - keep loading tokens until a certain size, merge that data to the files, and then continue parsing data
3. choose/write html parser for the above module.
    - must be able to handle broken html
    - can BeautifulSoup and lxml handle broken html?

### Milestone 2

4. write cython module to search/query Matrix

### Milestone 3