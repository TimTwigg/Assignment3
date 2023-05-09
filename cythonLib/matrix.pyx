class Matrix:
    def __init__(self):
        self._matrix_: dict[str: list[str]] = {}
    
    def __str__(self) -> str:
        return str(self._matrix_)
    
    def add(self, str term, str docID) -> None:
        """Insert a new document to the matrix for the given term.
        Adds the term if it does not yet exist in the matrix.
        
        Args:
            term (str): the term to create or update
            docID (str): the id to add to term's value
        """
        if term in self._matrix_:
            self._matrix_[term].append(docID)
        else:
            self._matrix_[term] = [docID]
    
    def remove(self, str term, str docID = "") -> None:
        """Remove a term or docID from the matrix. If docID is None,
        remove the entire term, else remove docID from term's value.

        Args:
            term (str): the term to update or delete
            docID (str, optional): the id to add to term's value
        """
        pass
    
    def find(self, query: list) -> list:
        """Query the matrix for a document that matches all terms in query.

        Args:
            query (list[str]): the list of string terms to match
        
        Returns:
            (list[str]): the list of document ids that matched
        """
        pass