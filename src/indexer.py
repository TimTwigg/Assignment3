from pathlib import Path
from bs4 import BeautifulSoup, MarkupResemblesLocatorWarning
from bs4.builder import XMLParsedAsHTMLWarning
import warnings
import json
import re
from nltk.stem import SnowballStemmer
import openai
import os
from enum import Enum
from src.helpers import tokenize, tag_visible, computeWordFrequencies, simhash, simHashSimilarity
from src.config import Config

warnings.filterwarnings("ignore", category = XMLParsedAsHTMLWarning)
warnings.filterwarnings("ignore", category = MarkupResemblesLocatorWarning)

openai.organization = "org-2egDI4pNkT6wiQgGhN5anyC6"
openai.api_key = os.getenv("OPENAI_API_KEY")

SMALL_DATASET_ROOT = "data/analyst_dataset"
LARGE_DATASET_ROOT = "data/developer_dataset"

class TagType(Enum):
    TITLE = 0
    HEADER = 1
    BOLD = 2

class Site:
    def __init__(self, path: Path, tokens: dict[str: int], url: str, headers: set[str], bold: set[str], titles: set[str], title: str, summary: str):
        self.path: Path = path
        self.tokens: dict[str: int] = tokens
        self.url: str = url
        self.titles: set[str] = titles
        self.headers: set[str] = headers
        self.bold: set[str] = bold
        self.title: str = title
        self.summary: str = summary

class Indexer:
    def __init__(self, dataset: str = "test", summaries: bool = False):
        """Create Indexer

        Args:
            dataset (str, optional): 'large' or 'test'. Which dataset to run on. Defaults to 'test'. \n
            summaries (bool, optional): whether to use the openai api to summarize the page. Defaults to False.
        """
        if dataset == "large":
            self._dataset = LARGE_DATASET_ROOT
        else:
            self._dataset = SMALL_DATASET_ROOT

        self._getNextUrl = (url for url in Path(self._dataset).glob("**/*.json"))
        self.stemmer = SnowballStemmer("english")
        self.config = Config()
        self.simHashes: set[int] = set()
        self.summaries: bool = summaries
        self.links: dict[int: list[set[int], int]] = {}
    
    def _validate_filetype_(self, url: str) -> bool:
        """Returns False if the url has an invalid filetype, else True."""
        return not re.match(r".*\.(txt|log|xml|git)", url.lower())
    
    def _parse_html_(self, html: str) -> tuple[list[str], set[str], set[str], set[str], str, set[str]]:
        soup = BeautifulSoup(html, "lxml")
        
        # extract all visible text segments
        texts: list[str] = []
        tokens: list[str] = []
        for t in soup.findAll(string = True):
            if tag_visible(t):
                texts.append(t)
                # tokenize and stem the text segments
                for tok in tokenize(t):
                    tokens.append(self.stemmer.stem(tok))
        
        headers: set[str] = set()
        bold: set[str] = set()
        titles: set[str] = set()
        title: list[str] = []
        links: set[str] = set()
        
        for tag in soup.find_all(re.compile(r"^(h[1-3]|b|strong|title|a)$")):
            if tag.name == "a":
                links.add(tag.get("href"))
                continue
            elif tag.name == "title":
                title.append(tag.text)
                tagtype = TagType.TITLE
            elif tag.name in ("b", "strong"):
                tagtype = TagType.BOLD
            elif tag.name.startswith("h"):
                tagtype = TagType.HEADER
            else:
                raise Exception()
            for tok in tokenize(tag.text):
                match tagtype:
                    case TagType.TITLE:
                        titles.add(self.stemmer.stem(tok))
                    case TagType.BOLD:
                        bold.add(self.stemmer.stem(tok))
                    case TagType.HEADER:
                        headers.add(self.stemmer.stem(tok))
        
        return tokens, headers, bold, titles, None if len(title) < 1 else title[0], self.summarize(". ".join(texts)), links
    
    def _sim_in_set_(self, sim: int) -> bool:
        if sim in self.simHashes:
            return True
        if self.config.sim_thresh < 1:
            for s in self.simHashes:
                if simHashSimilarity(sim, s) > self.config.sim_thresh:
                    return True
        self.simHashes.add(sim)
        return False
    
    def summarize(self, text: str) -> str:
        if not self.summaries:
            return ""
        
        response = openai.Completion.create(
            engine = "text-davinci-003",
            prompt = f"Summarize this text using less than 40 words:\n{text[:2048]}\nSummary:",
            temperature = 0.5,
            max_tokens = 40,
            n = 1,
            stop = None
        )
        return response.choices[0].text.strip()
    
    def _add_links_(self, url: str, links: set[str]):
        id = hash(url)
        idSet = set(hash(i) for i in links)
        if id not in self.links:
            self.links[id] = [set(), len(links)]
        else:
            self.links[id][1] += len(links)
        for l in idSet:
            if l not in self.links:
                self.links[l] = [set(), 0]
            self.links[l][0].add(id)
    
    def _tokenize_(self, url: Path) -> tuple[dict[str: int], str, set[str], set[str], set[str], str, str] | None:
        # load file
        with url.open("r") as f:
            data = json.loads(f.read())
        # skip certain file types
        if not self._validate_filetype_(data["url"].split("#")[0]):
            return None
        # parse html
        *tokens, links = self._parse_html_(data["content"])
        # compute frequencies
        freqs = computeWordFrequencies(tokens[0])
        # check simhash
        if self._sim_in_set_(simhash(tokens[0], freqs)):
            return None
        # add links
        self._add_links_(data["url"].split("#")[0], links)
        
        return freqs, data["url"].split("#")[0], *tokens[1:]
    
    def getLinks(self) -> dict[int: tuple[set[int], int]]:
        return self.links
    
    def getNextSite(self) -> Site:
        try:
            file = next(self._getNextUrl)
        except StopIteration:
            return None
        parts = self._tokenize_(file)
        if parts is None:
            return self.getNextSite()
        return Site(file, *parts)
