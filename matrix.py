from __future__ import annotations
from dataclasses import dataclass
from sortedcontainers import SortedList

@dataclass(order = True)
class Posting:
    id: str
    frequency: int
    
    def __eq__(self, other: Posting) -> bool:
        return self.id == other.id

    def __ne__(self, other: Posting) -> bool:
        return not self == other
    
    def __lt__(self, other: Posting) -> bool:
        return self != other and self.frequency < other.frequency
    
    def __le__(self, other: Posting) -> bool:
        return self == other or self < other
    
    def __gt__(self, other: Posting) -> bool:
        return self != other and self.frequency > other.frequency
    
    def __ge__(self, other: Posting) -> bool:
        return self == other or self > other
    
    def __add__(self, other: Posting) -> Posting:
        return Posting(self.id, self.frequency + other.frequency)
    
    def __iadd__(self, other: Posting) -> Posting:
        self.frequency += other.frequency
        return self

class Matrix:
    def __init__(self):
        self._matrix_: dict[str: SortedList[Posting]] = {}
    
    def __str__(self) -> str:
        return str(self._matrix_)

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
                    self._matrix_[term][i] += post
                else:
                    self._matrix_[term].remove(post)
                    self._matrix_[term].append(post)
            else:
                self._matrix_[term].append(post)
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
            i = self._matrix_[term].index(postID)
            t = self._matrix_[term][i]
            self._matrix_[term].remove(t)
        return t