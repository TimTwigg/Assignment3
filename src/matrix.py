from __future__ import annotations
from dataclasses import dataclass
from sortedcontainers import SortedList
import json

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
    def __init__(self, data: MatrixData = {}):
        """Create a new Matrix object.

        Args:
            data (MatrixData, optional): if provided, creates the Matrix from the given previous matrix data.
        """
        self._matrix_: MatrixData = data
    
    def __str__(self) -> str:
        return "\n  ".join(["Matrix:"] + [f"{k}: {v}" for k,v in self._matrix_.items()])

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
        if term in self._matrix_:
            if post in self._matrix_[term]:
                if update:
                    i = self._matrix_[term].index(post)
                    self._matrix_[term][i].frequency += post.frequency
                else:
                    self._matrix_[term].discard(post)
                    self._matrix_[term].add(post)
            else:
                self._matrix_[term].add(post)
        else:
            self._matrix_[term] = SortedList([post])
    
    def remove(self, term: str, postID: str = None) -> Posting|SortedList[Posting]:
        """Remove a term or post from the matrix. If postID is None, remove
        the entire term, else remove the posting with postID from term's value.

        Args:
            term (str): the term to update or delete. \n
            postID (str, optional): id of Posting to remove. Defaults to None.

        Returns:
            Posting|SortedList[Posting]: the Posting or list of Postings removed.
        """
        if postID is None:
            t = self._matrix_[term]
            del self._matrix_[term]
        else:
            i = self._matrix_[term].index(Posting(postID, 0))
            t = self._matrix_[term][i]
            self._matrix_[term].discard(t)
        return t
    
    def size(self) -> int:
        return len(self._matrix_)
    
    def save(self, filename: str = "matrix.json") -> None:
        """Save the matrix to a json file.

        Args:
            filename (str, optional): filename to save to. Defaults to "matrix.json".
        """
        with open(filename, "w") as f:
            json.dump({k: [p.toDict() for p in v] for k,v in self._matrix_.items()}, f, indent = 4)
    
    @staticmethod
    def load(filename: str = "matrix.json") -> Matrix:
        """Load a matrix from a save file.

        Args:
            filename (str, optional): the filename to load from. Defaults to "matrix.json".

        Returns:
            Matrix: a new Matrix object with the loaded data.
        """
        try:
            with open(filename, "r") as f:
                data: MatrixData = json.load(f)
            return Matrix(data)
        except FileNotFoundError:
            raise MatrixException(f"Could not find file to load Matrix: {filename}")