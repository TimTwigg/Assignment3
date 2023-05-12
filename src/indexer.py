from pathlib import Path
from bs4 import BeautifulSoup
from bs4.builder import XMLParsedAsHTMLWarning
import warnings
import json
from dataclasses import dataclass
from nltk.stem import PorterStemmer
from src.helpers import tokenize, tag_visible, computeWordFrequencies

warnings.filterwarnings("ignore", category = XMLParsedAsHTMLWarning)

SMALL_DATASET_ROOT = "data/analyst_dataset"
LARGE_DATASET_ROOT = "data/developer_dataset"
STOP_WORDS_FILE = "data/stop_words.txt"

@dataclass
class Site:
    path: Path
    tokens: dict[str: int]

class Indexer:
    def __init__(self, dataset: str = "test"):
        """Create Indexer

        Args:
            dataset (str, optional): 'large' or 'test'. Which dataset to run on. Defaults to 'test'.
        """
        if dataset == "large":
            self._dataset = LARGE_DATASET_ROOT
        else:
            self._dataset = SMALL_DATASET_ROOT

        self._getNextUrl = (url for url in Path(self._dataset).glob("**/*.json"))
        self.stemmer = PorterStemmer()
    
    def _parse_html_(self, html: str) -> list:
        soup = BeautifulSoup(html, "lxml")
        texts = [t for t in soup.findAll(string = True) if tag_visible(t)]
        tokens = [self.stemmer.stem(tok) for t in texts for tok in tokenize(t)]
        return tokens
    
    def _tokenize_(self, url: Path) -> dict[str: int]:
        with url.open("r") as f:
            data = json.loads(f.read())
        html: str = data["content"]
        tokens = self._parse_html_(html)
        return computeWordFrequencies(tokens)
    
    def getNextSite(self) -> Site:
        try:
            url = next(self._getNextUrl)
        except StopIteration:
            return None
        return Site(url, self._tokenize_(url))