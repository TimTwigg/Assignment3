from bs4.element import Comment, NavigableString
import re

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
    if element.parent.name in ["style", "script", "head", "meta", "[document]"]:
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