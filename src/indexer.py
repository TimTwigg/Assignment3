from pathlib import Path
from bs4 import BeautifulSoup, MarkupResemblesLocatorWarning
from bs4.builder import XMLParsedAsHTMLWarning
import warnings
import json
import re
from typing import Tuple
from nltk.stem import SnowballStemmer
from src.helpers import tokenize, tag_visible, computeWordFrequencies

warnings.filterwarnings("ignore", category = XMLParsedAsHTMLWarning)
warnings.filterwarnings("ignore", category = MarkupResemblesLocatorWarning)

SMALL_DATASET_ROOT = "data/analyst_dataset"
LARGE_DATASET_ROOT = "data/developer_dataset"

class Site:
    def __init__(self, path: Path, tokens: dict[str: int], url: str, headers: set[str], bold: set[str], titles: set[str]):
        self.path: Path = path
        self.tokens: dict[str: int] = tokens
        self.url: str = url
        self.titles: set[str] = titles
        self.headers: set[str] = headers
        self.bold: set[str] = bold

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
        self.stemmer = SnowballStemmer("english")
    
    def _parse_html_(self, html: str) -> Tuple[list, set, set, set]:
        soup = BeautifulSoup(html, "lxml")
        
        # extract all visible text segments
        texts = [t for t in soup.findAll(string = True) if tag_visible(t)]
        # stem and tokenize the text segments
        tokens = [self.stemmer.stem(tok) for t in texts for tok in tokenize(t)]
        # find headers
        headers = set(self.stemmer.stem(tok) for t in soup.find_all(re.compile("^h[1-3]$")) for tok in tokenize(t.text))
        # find bold
        bold = set(self.stemmer.stem(tok) for t in soup.find_all(re.compile("^(b|strong)$")) for tok in tokenize(t.text))
        # find titles
        titles = set(self.stemmer.stem(tok) for t in soup.find_all(re.compile("^title$")) for tok in tokenize(t.text))
        
        return tokens, headers, bold, titles
    
    def _tokenize_(self, url: Path) -> Tuple[dict[str: int], str, set[str], set[str], set[str]]:
        # load file
        with url.open("r") as f:
            data = json.loads(f.read())
        # get html content
        html: str = data["content"]
        # parse html
        tokens = self._parse_html_(html)
        return computeWordFrequencies(tokens[0]), data["url"], *tokens[1:]
    
    def getNextSite(self) -> Site:
        try:
            file = next(self._getNextUrl)
        except StopIteration:
            return None
        return Site(file, *self._tokenize_(file))