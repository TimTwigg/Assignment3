from __future__ import annotations
from dataclasses import dataclass
from sortedcontainers import SortedList
import json
from json import JSONDecodeError
from copy import deepcopy
from pathlib import Path

class MatrixException(Exception):
    pass

@dataclass(order = True)
class Posting:
    id: int
    frequency: int
    
    def __init__(self, id: int, frequency: int):
        if not isinstance(id, int):
            # raise MatrixException("Posting id must be int")
            id = int(id)
        elif not isinstance(frequency, int):
            raise MatrixException("Posting frequency must be int")
        
        self.id = id
        self.frequency = frequency
    
    def __eq__(self, other: Posting) -> bool:
        return isinstance(other, Posting) and self.id == other.id

    def __ne__(self, other: Posting) -> bool:
        return not self == other
    
    def __add__(self, other: Posting) -> Posting:
        return Posting(self.id, self.frequency + other.frequency)
    
    def __iadd__(self, other: Posting) -> Posting:
        self.frequency += other.frequency
        return self
    
    def __str__(self) -> str:
        return f"Posting(id={self.id}, frequency={self.frequency})"
    
    def toDict(self) -> dict:
        return {"id": self.id, "frequency": self.frequency}

MatrixData = dict[str: SortedList[Posting]]

class Matrix:
    def __init__(self, data: list[MatrixData] = [], folder: str = "index", filename: str = "matrix", breakpoints: list[str] = ["a", "i", "r"], clean: bool = False):
        """Create a new Matrix object.

        Args:
            data (MatrixData, optional): if provided, creates the Matrix from the given previous matrix data.
            folder (str, optional): folder where index is stored. Defaults to "index".
            filename (str, optional): the filename for the matrix files. Defaults to "matrix".
            breakpoints (list[str], optional): the breakpoints to segment the matrix on. Defaults to ["a", "i", "r"].
            clean (bool, optional): whether to delete the index files (if exist) on matrix initiation. Defaults to False.
        """
        self._breakpoints_ = breakpoints
        self._matrix_count_ = len(self._breakpoints_) + 1
        self._submatrices_: dict[int: MatrixData] = {i: {} for i in range(self._matrix_count_)}
        self._sizes_: list[int] = [0 for _ in range(self._matrix_count_)]
        self._filename_ = filename
        self._root_ = folder
        
        # create folder
        path = Path() / self._root_
        path.mkdir(exist_ok = True)
        
        # load init data
        try:
            for m in data:
                for k,v in m.items():
                    for post in v:
                        self.add(k, Posting(**post))
        except (IndexError, KeyError):
            raise MatrixException("Matrix: invalid data.")
        
        if clean:
            self._clean_submatrices_()
    
    def _clean_submatrices_(self) -> None:
        for i in range(self._matrix_count_):
            path = Path(f"{self._root_}/{self._filename_}{i}.json")
            path.unlink(missing_ok = True)
    
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
        if term in matrix:
            if post in matrix[term]:
                if update:
                    i = matrix[term].index(post)
                    matrix[term][i].frequency += post.frequency
                else:
                    matrix[term].discard(post)
                    matrix[term].add(post)
            else:
                matrix[term].add(post)
        else:
            matrix[term] = SortedList([post])
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
    
    def _remove_(self, id: int, matrix: MatrixData, term: str, postID: int = None) -> Posting|SortedList[Posting]:
        try:
            if postID is None:
                t = matrix[term]
                del matrix[term]
                self._increment_size(id, -1)
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
        """Returns true total size of the matrix, including matrix sections offloaded to files. First offloads any data currently in matrix."""
        self.save()
        size = 0
        for i in range(self._matrix_count_):
            data = self._load_submatrix_(i)
            size += len(data)
        return size
    
    def save(self) -> None:
        """Save the matrix to json files."""
        meta = {
            "filename": self._filename_,
            "breakpoints": self._breakpoints_
        }
        with open(f"{self._root_}/meta.json", "w") as f:
            json.dump(meta, f, indent = 4)
        
        for i in range(self._matrix_count_):
            data = self._load_submatrix_(i)
            with open(f"{self._root_}/{self._filename_}{i}.json", "w") as f:
                json.dump({k: [p.toDict() for p in v] for k,v in self._merge_matrices_(data, self._submatrices_[i]).items()}, f, indent = 4)
                self._submatrices_[i].clear()
                self._sizes_[i] = 0
    
    def _load_submatrix_(self, id: int) -> MatrixData:
        """Load a partial matrix.

        Args:
            id (int): the submatrix number to load.

        Raises:
            MatrixException: if id is invalid.

        Returns:
            MatrixData: the loaded submatrix.
        """
        if not isinstance(id, int) or id < 0 or id > self._matrix_count_:
            raise MatrixException(f"_load_submatrix_: invalid id: {id}")
        
        path = Path(f"{self._root_}/{self._filename_}{id}.json")
        path.touch()
        with open(f"{self._root_}/{self._filename_}{id}.json", "r") as f:
            try:
                data = json.loads(f.read())
            except JSONDecodeError:
                data = {}
        
        return {k: SortedList((Posting(**p) for p in v)) for k,v in data.items()}
    
    def _merge_matrices_(self, matrixA: MatrixData, matrixB: MatrixData) -> MatrixData:
        """Merges two MatrixData matrices. Leaves both input matrices untouched.

        Args:
            matrixA (MatrixData): the first matrix
            matrixB (MatrixData): the second matix
        
        Raises:
            MatrixException: if either input matrix is None

        Returns:
            MatrixData: the resultant merged matrix.
        """
        if matrixA is None or matrixB is None:
            raise MatrixException("_merge_matrices: Can't merge None")
        
        matrix = deepcopy(matrixA)
        for k,v in matrixB.items():
            for post in v:
                if k not in matrix:
                    matrix[k] = SortedList([post])
                    continue
                
                if post in matrix[k]:
                    matrix[k][matrix[k].index(k)].frequency += post.frequency
                else:
                    matrix[k].add(post)
        return matrix
    
    @staticmethod
    def load(folder: str = "index") -> Matrix:
        """Load a matrix from save files.

        Args:
            folder (str, optional): the folder containing the matrix. Defaults to "index".

        Returns:
            Matrix: a new Matrix object with the loaded data.
        """
        data = []
        count = 0
        try:
            with open(f"{folder}/meta.json", "r") as f:
                meta: dict = json.load(f)
        except FileNotFoundError:
            raise MatrixException(f"Index metadata not found at: {folder}")
        
        while True:
            try:
                with open(f"{folder}/{meta['filename']}{count}.json", "r") as f:
                    data.append(json.load(f))
            except FileNotFoundError:
                break
            except JSONDecodeError:
                pass
            count += 1
        return Matrix(data, folder, meta["filename"], meta["breakpoints"])