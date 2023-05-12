import re

# word = re.compile(r"[0-9A-Za-z']+")
word = re.compile(r"\w+")
s = '''Good muffins cost $3.88\nin New York.  Please buy me
two of them.\n\nThanks. I can't tell you'''
print(word.findall(s))