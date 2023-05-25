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
4. write module to search/query Matrix[`done`]
    - write in python [`done`]
    - convert to cython for faster querying?

### Milestone 3

5. updating the index
    - don't edit the original index. maintain extra indeces for updated and deleted pages.
        - when the index is queried, check the results against the updated/deleted pages indeces.
6. index todo
    - modify index to take text location into account so that bold/header/title text can be separated as important [`done`]
        - could just add boolean fields to Posting marking whether the word appeared in important fields [`done`]
            - one for each type so that they can be weighted differently? [`done`]
7. query caching [`done']
8. optimization
    - rework index files as csv files with [term, postings] rows [`done`]
        - would allow partial loading of file instead of whole thing, plus no json decoding [`done`]
        - term would be str, postings could be stringified json dict to be decoded if necessary [`done`]
    - rework indexing to save partials and merge at the end rather than loading/merging/dumping each time [`done`]
    - use linecache module to jump to certain lines? [`done`]
        - would need another index rework [`done`]
        - achieved with file.seek [`done`]
    - conjunctive processing [`done`]
    - tiered indeces?
        - extra segmented for each token to make it easy to find the best n pages for each token
    - streamline index file loading [`done`]
    - add document similarity checking to indexing?
    - initally ignore stop words in query [`done`]
        - go back and use them if we don't have enough results without them [`done`]
    - thresholding
        - lecture 19
    - sort posting lists by importance for that term and then read only the first x postings?
        - could speed up processing
        - unsafe
    - multithreading
        - give each term to a different thread?
9. ranked retrieval
    - add more info to Posting
        - use tf-idf score instead of term frequency
    - Pagerank idea: maintain extra index of [docID -> rank]?
    - Jaccard coefficient: intersection / union of 2 sets
    - relevance score
        - R(Q, D) -> score
        - each part of the score is multiplied by a weight
        - the weights should sum to 1 (set int values then normalize to proportion of weight)
10. gui
    - make it
    - make NotFound page for when no results are found