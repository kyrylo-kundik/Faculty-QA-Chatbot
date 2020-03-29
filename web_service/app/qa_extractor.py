import collections
import re
from typing import List

import requests


class QAExtractor:
    QAContent = collections.namedtuple("QAContent", "question answer")

    def __init__(self, txt_url: str):
        self.txt_url = txt_url
        self._rex_pattern = r"\n\d{1,10}\."

    def parse(self) -> List[QAContent]:
        text = requests.get(self.txt_url).text
        result = []

        splitted = re.split(self._rex_pattern, text)

        for i, split in enumerate(splitted, start=1):
            if split == "":
                continue

            split = split.split("\n", 1)
            result.append(self.QAContent(question=split[0].strip(), answer=split[1].strip()))

        return result


if __name__ == "__main__":
    qa = QAExtractor(
        "https://docs.google.com/document/u/0/export?format=txt&id=1L0gZPdC-66Jt_Wqo9Eu_"
        "s2SsunyOMtkP52byRQCdE1Q&token=AC4w5VhqUsZBi5pYGT1ST1GRlB1RuuwbLw%3A1585500029845"
        "&includes_info_params=true"
    ).parse()

    for parsed in qa:
        print(f"Question: {parsed.question}\nAnswer: {parsed.answer}\n\n\n")

    print(len(qa))
