from bs4.element import Comment, NavigableString
import re
import hashlib

def tokenize(input_str: str) -> list[str]:
    """File Tokenizer

    Args:
        input_str (str): str to tokenize

    Returns:
        str: the next token
    """
    WORD = re.compile(r"[\w+]+")
    return WORD.findall(input_str)

def tag_visible(element: NavigableString) -> bool:
    """Checks if the given element is a visible tag.

    Args:
        element (NavigableString): the BeautifulSoup NavigableString to check.

    Returns:
        bool: True if element is visible to users when the page is rendered, else False
    """
    if element.parent.name in ["style", "script", "head", "meta", "[document]", "a", "img"]:
        return False
    if isinstance(element, Comment):
        return False
    return True

def computeWordFrequencies(tokens: list[str]) -> dict[str:int]:
    """Computes the frequencies of each token in the tokens list

    Args:
        tokens (list[str]): the list of string tokens

    Returns:
        dict[str:int]: the dictionary containing (token: frequency) items
    """
    freq = {}
    for tok in tokens:
        freq[tok] = freq.get(tok, 0) + 1
    return freq

def getMult(num: int, i: int) -> int:
    """Return 1 if the i'th bit is 1, else -1"""
    return 1 if (num >> i) & 1 else -1

def simhash(tokens: list[str], frequencies: dict[str: int]) -> int:
    """Compute the SimHash for a document.

    Args:
        tokens (list[str]): the tokens in the document.
        frequencies (dict[str:int]): the token frequencies dict.

    Returns:
        int: the integer SimHash
    """    
    uTokens = list(set(tokens))
    hashes: list[tuple[str, int]] = [(t, int.from_bytes(hashlib.sha1(t.encode("utf-8")).digest()[:8], "little")) for t in uTokens]
    # longer calculation using nested loops proved faster than the shorter version which used the built-in sum function
    v = []
    for i in range(64):
        total = 0
        for t,h in hashes:
            total += getMult(h, i)*frequencies[t]
        v.append(1 if total > 0 else 0)
    # convert to binary
    res = 0
    for ele in v:
        res = (res << 1) | ele
    return res

def simHashSimilarity(s1: int, s2: int) -> float:
    """Compute the similarity score for two SimHashes.

    Args:
        s1 (int): the first SimHash int
        s2 (int): the second SimHash int

    Returns:
        float: the similarity score
    """
    return sum(1 if (s1 >> i) & 1 == (s2 >> i) & 1 else 0 for i in range(64)) / 64