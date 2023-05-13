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
    id: str
    frequency: int
    
    def __init__(self, id: str, frequency: int):
        if not isinstance(id, str):
            raise MatrixException("Posting id must be str")
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
    def __init__(self, data: list[MatrixData] = [], filename: str = "matrix"):
        """Create a new Matrix object.

        Args:
            data (MatrixData, optional): if provided, creates the Matrix from the given previous matrix data.
            filename (str, optional): the filename for the matrix files. Defaults to 'matrix'.
        """
        self._breakpoints_ = ["a", "i", "r"]
        self._matrix_1_: MatrixData = {}
        self._matrix_2_: MatrixData = {}
        self._matrix_3_: MatrixData = {}
        self._matrix_4_: MatrixData = {}
        self._matrix_1_size_: int = 0
        self._matrix_2_size_: int = 0
        self._matrix_3_size_: int = 0
        self._matrix_4_size_: int = 0
        self._filename_ = filename
        
        # load init data
        try:
            for m in data:
                for k,v in m.items():
                    for post in v:
                        self.add(k, post)
        except (IndexError, KeyError):
            raise MatrixException("Matrix: invalid data.")
        
        self._clean_submatrices_()
    
    def _clean_submatrices_(self) -> None:
        for i in range(1, 5):
            path = Path(f"{self._filename_}{i}.json")
            path.unlink(missing_ok = True)
    
    def __str__(self) -> str:
        return "\n  ".join(["Matrix:"] + [f"{k}: {v}" for k,v in self._matrix_1_.items()] + ["+"] +
                           [f"{k}: {v}" for k,v in self._matrix_2_.items()] + ["+"] +
                           [f"{k}: {v}" for k,v in self._matrix_3_.items()] + ["+"] +
                           [f"{k}: {v}" for k,v in self._matrix_4_.items()]) + "\n"
    
    def _increment_size(self, id: int, modifier: int = 1) -> None:
        match id:
            case 1:
                self._matrix_1_size_ += 1 * modifier
            case 2:
                self._matrix_2_size_ += 1 * modifier
            case 3:
                self._matrix_3_size_ += 1 * modifier
            case 4:
                self._matrix_4_size_ += 1 * modifier
    
    def _choose_submatrix_(self, term: str) -> int:
        """Determines which submatrix the term should fit into.

        Args:
            term (str): The term to test.

        Returns:
            int: an int in the range [1, 4] representing which submatrix the term belongs to.
        """
        for i,brk in enumerate(self._breakpoints_, start = 1):
            if term < brk:
                return i
        return 4
    
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
        match brk:
            case 1:
                self._add_(1, self._matrix_1_, term, post, update)
            case 2:
                self._add_(2, self._matrix_2_, term, post, update)
            case 3:
                self._add_(3, self._matrix_3_, term, post, update)
            case 4:
                self._add_(4, self._matrix_4_, term, post, update)
    
    def _remove_(self, id: int, matrix: MatrixData, term: str, postID: str = None) -> Posting|SortedList[Posting]:
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
    
    def remove(self, term: str, postID: str = None) -> Posting|SortedList[Posting]:
        """Remove a term or post from the matrix. If postID is None, remove
        the entire term, else remove the posting with postID from term's value.

        Args:
            term (str): the term to update or delete. \n
            postID (str, optional): id of Posting to remove. Defaults to None.

        Returns:
            Posting|SortedList[Posting]: the Posting or list of Postings removed.
        """
        brk: int = self._choose_submatrix_(term)
        try:
            match brk:
                case 1:
                    return self._remove_(1, self._matrix_1_, term, postID)
                case 2:
                    return self._remove_(2, self._matrix_2_, term, postID)
                case 3:
                    return self._remove_(3, self._matrix_3_, term, postID)
                case 4:
                    return self._remove_(4, self._matrix_4_, term, postID)
        except MatrixException:
            pass
    
    def size(self) -> int:
        """Returns the current size of the matrix. Does not include matrix sections offloaded to files."""
        return self._matrix_1_size_ + self._matrix_2_size_ + self._matrix_3_size_ + self._matrix_4_size_
    
    def scan_size(self) -> int:
        """Returns true total size of the matrix, inclduing matrix sections offloaded to files. First offloads any data currently in matrix."""
        self.save()
        size = 0
        for i in range(1, 5):
            data = self._load_submatrix_(i)
            size += len(data)
        return size
    
    def save(self) -> None:
        """Save the matrix to json files."""
        data = self._load_submatrix_(1)
        with open(self._filename_ + "1.json", "w") as f:
            json.dump({k: [p.toDict() for p in v] for k,v in self._merge_matrices_(data, self._matrix_1_).items()}, f, indent = 4)
            self._matrix_1_.clear()
            self._matrix_1_size_ = 0
        
        data = self._load_submatrix_(2)
        with open(self._filename_ + "2.json", "w") as f:
            json.dump({k: [p.toDict() for p in v] for k,v in self._merge_matrices_(data, self._matrix_2_).items()}, f, indent = 4)
            self._matrix_2_.clear()
            self._matrix_2_size_ = 0
        
        data = self._load_submatrix_(3)
        with open(self._filename_ + "3.json", "w") as f:
            json.dump({k: [p.toDict() for p in v] for k,v in self._merge_matrices_(data, self._matrix_3_).items()}, f, indent = 4)
            self._matrix_3_.clear()
            self._matrix_3_size_ = 0
        
        data = self._load_submatrix_(4)
        with open(self._filename_ + "4.json", "w") as f:
            json.dump({k: [p.toDict() for p in v] for k,v in self._merge_matrices_(data, self._matrix_4_).items()}, f, indent = 4)
            self._matrix_4_.clear()
            self._matrix_4_size_ = 0
    
    def _load_submatrix_(self, id: int) -> MatrixData:
        """Load a partial matrix.

        Args:
            id (int): the submatrix number to load.

        Raises:
            MatrixException: if id is invalid.

        Returns:
            MatrixData: the loaded submatrix.
        """
        if not isinstance(id, int) or id < 1 or id > 4:
            raise MatrixException(f"_load_submatrix_: invalid id: {id}")
        
        path = Path(f"{self._filename_}{id}.json")
        path.touch()
        with open(f"{self._filename_}{id}.json", "r") as f:
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
    def load(filename: str = "matrix") -> Matrix:
        """Load a matrix from save files.

        Args:
            filename (str, optional): the filename to load from. Defaults to "matrix".

        Returns:
            Matrix: a new Matrix object with the loaded data.
        """
        try:
            with open(f"{filename}1.json", "r") as f:
                data1 = json.load(f)
            with open(f"{filename}2.json", "r") as f:
                data2 = json.load(f)
            with open(f"{filename}3.json", "r") as f:
                data3 = json.load(f)
            with open(f"{filename}4.json", "r") as f:
                data4 = json.load(f)
            return Matrix([data1, data2, data3, data4], filename)
        except FileNotFoundError:
            raise MatrixException(f"Could not find file to load Matrix: {filename}")