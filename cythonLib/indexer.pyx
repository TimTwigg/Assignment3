# module to index the dataset
# test on the small dataset since the large one will probably take a while to run
# actual index creation MUST be done with the large dataset since we are a CS group

from pathlib import Path

SMALL_DATASET_ROOT = "data/analyst_dataset"
LARGE_DATASET_ROOT = "data/developer_dataset"

# TokenSet = TypeVar("TokenSet", dict[str:int])

class Site:
    url: str
    tokens: dict[str, int]

    def __init__(self, url: str, tokens: dict) -> None:
        self.url = url
        self.tokens = tokens
    
    def __str__(self) -> str:
        return f"{self.url}: {self.tokens}"

class Indexer:
    dataset: str

    def __init__(self, dataset: str = "test"):
        """Create Indexer

        Args:
            dataset (str, optional): 'large' or 'test'. Which dataset to run on. Defaults to 'test'.
        """
        if dataset == "large":
            self.dataset = LARGE_DATASET_ROOT
        else:
            self.dataset = SMALL_DATASET_ROOT
    
    def _getNextUrl_(self) -> str:
        return ""
    
    def _tokenize_(self, url: str) -> dict:
        return {}
    
    def getNextSite(self) -> Site:
        url = self._getNextUrl_()
        return Site(url, self._tokenize_(url))