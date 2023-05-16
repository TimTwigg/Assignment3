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
    - update save/load methods to work with a segmented matrix (see task 2) [`done`]
    - test methods more (even the ones not really going to be used too much such as adding a Posting that is already in the term's list) [`done`]
2. write python module to search datasets and add pages to the matrix [`done`]
    - indexer module in src [`done`]
    - implement `._getNextUrl_()`, `._parse_html_()` and `._tokenize_()` methods [`done`]
    - must not hold entire index in memory (segmented matrix) [`done`]
        - split into 3 or 4 sets of tokens alphabetically [`done`]
        - keep loading tokens until a certain size, merge that data to the files, and then continue parsing data [`done`]

### Milestone 2

3. update segmented matrix to work with an arbitrary number of breakpoints [`done`]
    - test increasing number of breakpoints and reducing chunk size on indexing speed. [`done`]
    - could have fewer segments during indexing and then split them afterwards for faster querying. [`done`]
    - set to create files in folder with extra metadata file for breakpoints and filecount? [`done`]
4. write module to search/query Matrix
    - write in python [`done`]
    - convert to cython for faster querying?

### Milestone 3

5. updating the index
    - don't edit the original index. maintain extra indeces for updated and deleted pages.
        - when the index is queried, check the results against the updated/deleted pages indeces.
6. query caching
7. optimization
    - conjunctive processing
    - tiered indeces
        - extra segmented for each token to make it easy to find the best n pages for each token
8. ranked retrieval
    - add more info to Posting
        - use tf-idf score instead of term frequency
    - Pagerank idea: maintain extra index of [docID -> rank]?
    - Jaccard coefficient: intersection / union of 2 sets