import re
from math import ceil


def split_and_divide(text) -> int:
    # text = "Visar 20 av totalt 2128"
    matches = re.findall(r"\d+", text)
    # Divide and round up
    return ceil(int(matches[1]) / int(matches[0]))
