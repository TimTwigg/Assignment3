from __future__ import annotations
from sortedcontainers import SortedList
from msgspec.json import decode
import json
import heapq
from pathlib import Path
import shutil
import csv
import math
import numpy as np

class MatrixException(Exception):
    pass

class Posting:
    def __init__(self, id: int, frequency: int, header: bool = False, bold: bool = False, title: bool = False):
        if not isinstance(id, int):
            raise MatrixException("Posting id must be int")
        elif not isinstance(frequency, int):
            raise MatrixException("Posting frequency must be int")
        
        self.id = id
        self.frequency = frequency
        self.header = header
        self.bold = bold
        self.title = title
    
    def __eq__(self, other: Posting) -> bool:
        return isinstance(other, Posting) and self.id == other.id

    def __ne__(self, other: Posting) -> bool:
        return not self == other
    
    def __lt__(self, other: Posting) -> bool:
        if not isinstance(other, Posting):
            raise NotImplementedError()
        return self.frequency < other.frequency
    
    def __le__(self, other: Posting) -> bool:
        return self == other or self < other
    
    def __gt__(self, other: Posting) -> bool:
        return not self <= other
    
    def __ge__(self, other: Posting) -> bool:
        return not self < other
    
    def __add__(self, other: Posting) -> Posting:
        return Posting(self.id, self.frequency + other.frequency)
    
    def __iadd__(self, other: Posting) -> Posting:
        self.frequency += other.frequency
        return self
    
    def __repr__(self) -> str:
        return f"Posting(id={self.id}, frequency={self.frequency})"
    
    def __hash__(self) -> int:
        return self.id
    
    def tf(self) -> int:
        """Return tf score of posting."""
        return min(1 + math.log10(self.frequency), self.frequency)
    
    def tf_norm(self, length: float) -> float:
        """Return the normalized tf score.

        Args:
            length (float): the normalized document length

        Returns:
            float: the normalized tf score
        """
        return min(1 + math.log10(self.frequency), self.frequency) / length
    
    def toDict(self) -> dict:
        return self.__dict__

MatrixData = dict[str: SortedList[Posting]]

class Matrix:
    def __init__(self, data: list[MatrixData] = [], documents: dict[int: str] = {}, folder: str = "index", filename: str = "matrix", breakpoints: list[str] = ["a", "i", "r"], clean: bool = False):
        """Create a new Matrix object.

        Args:
            data (MatrixData, optional): if provided, creates the Matrix from the given previous matrix data.
            documents (dict[int: str], optional): if provided, creates the Matrix with the given documents.
            folder (str, optional): folder where index is stored. Defaults to "index".
            filename (str, optional): the filename for the matrix files. Defaults to "matrix".
            breakpoints (list[str], optional): the breakpoints to segment the matrix on. Defaults to ["a", "i", "r"].
            clean (bool, optional): whether to delete the index files (if exist) on matrix initiation. Defaults to False.
        """
        self._breakpoints_ = breakpoints
        self._matrix_count_ = len(self._breakpoints_) + 1
        self._submatrices_: dict[int: MatrixData] = {i: {} for i in range(self._matrix_count_)}
        self._documents_: dict[int: str] = documents
        self._document_lengths_: dict[int: float] = {}
        self._document_titles_: dict[int: str] = {}
        self._document_summaries_: dict[int: str] = {}
        self._sizes_: list[int] = [0 for _ in range(self._matrix_count_)]
        self._filename_ = filename
        self._root_ = folder
        self._counter_: int = 0
        
        # clean folder
        p = Path(self._root_)
        if clean and p.exists():
            shutil.rmtree(p)
        p.mkdir(exist_ok = True)
        
        # load init data
        try:
            for m in data:
                for k,v in m.items():
                    for post in v:
                        self.add(k, Posting(**post))
        except (IndexError, KeyError):
            raise MatrixException("Matrix: invalid data.")
    
    def __str__(self) -> str:
        return "Matrix:\n" + "\n  +\n".join("\n  ".join([f"{k}: {v}" for k,v in m.items()]) for _,m in self._submatrices_.items())
    
    def _increment_size(self, id: int, modifier: int = 1) -> None:
        self._sizes_[id] += modifier
    
    def _choose_submatrix_(self, term: str) -> int:
        """Determines which submatrix the term should fit into.

        Args:
            term (str): The term to test.

        Returns:
            int: an int in the range [1, 4] representing which submatrix the term belongs to.
        """
        for i,brk in enumerate(self._breakpoints_):
            if term < brk:
                return i
        return self._matrix_count_ - 1
    
    def _add_(self, id: int, matrix: MatrixData, term: str, post: Posting, update: bool = True) -> None:
        # add a post to the given matrix for the given term
        if term in matrix:
            if post in matrix[term]:
                # if the document is already in the list for term
                if update:
                    i = matrix[term].index(post)
                    matrix[term][i].frequency += post.frequency
                else:
                    matrix[term].discard(post)
                    matrix[term].add(post)
            else:
                # if the document is not yet in the list for term
                matrix[term].add(post)
        else:
            # if the term is not in the matrix
            matrix[term] = SortedList([post], key = lambda x: x.tf())
            self._increment_size(id)

    def add(self, term: str, post: Posting, update: bool = True) -> None:
        """Insert a new document to the matrix for the given term.
        Adds the term if it does not yet exist in the matrix.
        
        If the post is in the term's list in the matrix already, adds
        the new post to the old one if update is True, otherwise replacing
        the original posting with the given post.

        Args:
            term (str): the term to create or update. \n
            post (Posting): the Posting to add to term's value. \n
            update (bool, optional): Sets behavior for post matching on insertion. Defaults to True.
        """
        brk: int = self._choose_submatrix_(term)
        self._add_(brk, self._submatrices_[brk], term, post, update)
        self._document_lengths_[post.id] += (1 + math.log10(post.frequency))**2
        
    def addDocument(self, docID: int, url: str, title: str, summary: str) -> None:
        """Add a document to the corpus.

        Args:
            docID (int): the id of the document \n
            url (str): the url of the document \n
            title (str): the document's title (if any) \n
            summary (str): the summary of the document
        """
        if docID not in self._documents_:
            self._documents_[docID] = url
            self._document_lengths_[docID] = 0
            self._document_titles_[docID] = "" if title is None else title
            self._document_summaries_[docID] = summary
    
    def _remove_(self, id: int, matrix: MatrixData, term: str, postID: int = None) -> Posting|SortedList[Posting]:
        # remove a post from term's list, or remove the term entirely.
        try:
            # remove the entire term
            if postID is None:
                t = matrix[term]
                del matrix[term]
                self._increment_size(id, -1)
            # remove just the post
            else:
                i = matrix[term].index(Posting(postID, 0))
                t = matrix[term][i]
                matrix[term].discard(t)
                if len(matrix[term]) == 0:
                    del matrix[term]
                    self._increment_size(id, -1)
            return t
        except ValueError:
            raise MatrixException(f"Not found in matrix: {term} with id {postID}")
    
    def remove(self, term: str, postID: int = None) -> Posting|SortedList[Posting]:
        """Remove a term or post from the matrix. If postID is None, remove
        the entire term, else remove the posting with postID from term's value.

        Args:
            term (str): the term to update or delete. \n
            postID (int, optional): id of Posting to remove. Defaults to None.

        Returns:
            Posting|SortedList[Posting]: the Posting or list of Postings removed.
        """
        try:
            brk: int = self._choose_submatrix_(term)
            return self._remove_(brk, self._submatrices_[brk], term, postID)
        except MatrixException:
            pass
    
    def size(self) -> int:
        """Returns the current size of the matrix. Does not include matrix sections offloaded to files."""
        return sum(self._sizes_)
    
    def scan_size(self) -> int:
        """Returns the number of unique tokens in the matrix files."""    
        size = 0
        for i in range(self._matrix_count_):
            with Path(f"{self._root_}/{self._filename_}{i}.csv").open(mode = "rb") as f:
                size += sum(1 for _ in f)
        return size
    
    def save(self) -> None:
        """Save the matrix to json files."""
        # dump index files
        for i in range(self._matrix_count_):
            with open(f"{self._root_}/{self._filename_}{i}_partial{self._counter_}.csv", mode = "w", encoding = "utf-8", newline = "") as f:
                writer = csv.writer(f)
                writer.writerows([k, *[json.dumps(p.toDict()) for p in v]] for k,v in self._submatrices_[i].items())
                self._submatrices_[i].clear()
                self._sizes_[i] = 0
        self._counter_ += 1
        
    def _index_matrix_(self) -> dict[str: int]:
        """Index the matrix.
        
        Returns:
            dict[str: int]: the index of [str -> byte position]
        """
        index = {}
        for i in range(self._matrix_count_):
            with open(f"{self._root_}/{self._filename_}{i}.csv", mode = "r", encoding = "utf-8") as f:
                while True:
                    pos = f.tell()
                    tokenID = f.readline().split(",")[0]
                    if len(tokenID.strip()) < 1:
                        break
                    index[tokenID] = [pos, i]
        return index
    
    def finalize(self, pageranks: dict[int: float], printing: bool = False) -> None:
        """Merge the partial matrices and save final index."""
        meta = {
            "filename": self._filename_,
            "documentCount": len(self._documents_),
            "breakpoints": self._breakpoints_
        }
        if printing:
            print("\nSaving Metadata...")
        # save metadata
        with open(f"{self._root_}/meta.json", "w") as f:
            json.dump(meta, f, indent = 4)
        
        if printing:
            print("Saving Documents...")
        # save documents
        with open(f"{self._root_}/documents.csv", newline = "", mode = "w", encoding = "utf-8") as f:
            writer = csv.writer(f, delimiter = ",")
            writer.writerows((i, d, math.sqrt(self._document_lengths_[i]), self._document_titles_[i], self._document_summaries_[i], pageranks[i]) for i,d in self._documents_.items())
        
        if printing:
            print("Merging Index...")
        # merge partials
        for i in range(self._matrix_count_):
            matrices = [self._load_submatrix_(i, p) for p in range(self._counter_)]
            matrix = self._merge_matrices_(matrices, pageranks)
            with open(f"{self._root_}/{self._filename_}{i}.csv", mode = "w", encoding = "utf-8", newline = "") as f:
                writer = csv.writer(f)
                writer.writerows([k, len(v), *[json.dumps(p.toDict()) for p in v]] for k,v in matrix.items())
        
        if printing:
            print("Cleaning Partial Indeces...")
        # delete partials
        for p in Path(self._root_).glob("*partial*.*"):
            p.unlink()
        
        # scan index and make index of index
        if printing:
            print("Indexing Index...")
        index = self._index_matrix_()
        
        # save index of index
        if printing:
            print("Saving Meta Index...")
        with open(f"{self._root_}/meta_index.json", "w") as f:
            json.dump(index, f, indent = 4)
    
    def _load_submatrix_(self, id: int, pid: int = None) -> MatrixData:
        """Load a partial matrix.

        Args:
            id (int): the submatrix number to load.
            pid (int): the partial id number of the submatrix to load.

        Raises:
            MatrixException: if id or pid is invalid.

        Returns:
            MatrixData: the loaded submatrix.
        """
        if not isinstance(id, int) or id < 0 or id > self._matrix_count_:
            raise MatrixException(f"_load_submatrix_: invalid id: {id}")
        elif pid is not None and (not isinstance(pid, int) or pid < 0 or pid >= self._counter_):
            raise MatrixException(f"_load_submatrix_: invalid pid: {pid}")
        
        if pid is not None:
            path = Path(f"{self._root_}/{self._filename_}{id}_partial{pid}.csv")
        else:
            path = Path(f"{self._root_}/{self._filename_}{id}.csv")
        path.touch()
        with path.open(mode = "r", encoding = "utf-8") as f:
            reader = csv.reader(f)
            data = {r[0]: [decode(i) for i in r[1:]] for r in reader}
        
        return {k: SortedList((Posting(**p) for p in v), key = lambda x: x.tf()) for k,v in data.items()}
    
    def _merge_matrices_(self, matrices: list[MatrixData], pageranks: dict[int: float]) -> MatrixData:
        """Merge a list of matrices.

        Args:
            matrices (list[MatrixData]): the list of submatrices to merge
            pageranks (dict[int: float]): the pageranks of all documents

        Returns:
            MatrixData: the resultant merged matrix.
        """
        
        matrix: dict[str: list[Posting]] = {}
        matrixItems = [sorted(m.items()) for m in matrices]
        temp: list[Posting] = []
        current: str = None
        
        if len(matrices) == 1:
            matrix = {}
            for k,v in matrices[0].items():
                matrix[k] = list(v)
        else:        
            # merge the sorted matrices with heapq and read in order
            for term,postings in heapq.merge(*matrixItems, key = lambda x: x[0]):
                # if it is a new term
                if current is None or term != current:
                    # if this is not the first one then save temp
                    if current is not None:
                        matrix[current] = temp
                    # reset temp and set current to the new term
                    temp = []
                    current = term
                # update temp
                temp.extend(postings)
            # save final temp
            matrix[current] = temp
        
        # sort document lists
        for k in matrix.keys():
            arr = np.array([i.tf() for i in matrix[k]])
            length = math.sqrt(np.sum(np.power(arr, 2)))
            matrix[k].sort(key = lambda x: (pageranks[x.id], x.tf_norm(length)), reverse = True)

        return matrix