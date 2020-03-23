import collections
import logging
import os
from io import StringIO
from typing import List

import requests
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage


class PDFExtractor:
    PageParagraphContent = collections.namedtuple("PageParagraphContent", "page_num paragraph_num content")

    def __init__(self, pdf_url="https://drive.google.com/u/0/uc?id=1aFsZWtcdv5chxCfs3Mhs22xrPSwdki8b&export=download"):
        self._pdf_url = pdf_url
        self._tmp_path = "tmp.pdf"
        self._max_page_num = 75
        self._min_page_num = 3
        self._words_threshold = 5

        self.escaped_strings: List[str] = [
            "Микола Глибовець. Справа МоГо життя – факультет інфорМатики наукМаМикола Глибовець. Справа МоГо життя – "
            "факультет інфорМатики наукМа",
            "- ",
            "Микола Глибовець. Справа МоГо життя – факультет інфорМатики наукМаПочаток роботи в наУКМА",
            "Микола Глибовець. Справа МоГо життя – факультет інфорМатики наукМа",
        ]

        self.parsed_content: List[PDFExtractor.PageParagraphContent] = []

        self._download_file()
        self.plain_text: str = self._convert_pdf_to_txt()

        self._filter_content()

        os.remove("tmp.pdf")

    def _download_file(self):
        logging.info(f"Started downloading PDF file from {self._pdf_url}")
        r = requests.get(self._pdf_url, stream=True)
        chunk_loaded = 0
        with open(self._tmp_path, "wb") as handle:
            for data in r.iter_content():
                chunk_loaded += len(data)
                handle.write(data)
        logging.info("Downloaded")

    def _convert_pdf_to_txt(self):
        rsrcmgr = PDFResourceManager()
        retstr = StringIO()
        codec = 'utf-8'
        laparams = LAParams()
        device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
        fp = open(self._tmp_path, 'rb')
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        password = ""
        maxpages = 0
        caching = True
        pagenos = set()
        text = ""
        page_num = 1
        for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password, caching=caching,
                                      check_extractable=True):
            interpreter.process_page(page)
            t = retstr.getvalue()
            text += t
            self._parse_page(t, page_num)
            retstr.truncate(0)
            retstr.seek(0)
            page_num += 1

        fp.close()
        device.close()
        retstr.close()
        return text

    def _parse_page(self, text, page_num):
        intermediate = []
        for data in text.split("\n\n"):
            paragraph = data \
                .replace(" \n", " ") \
                .replace("\n", " ") \
                .replace("\t ", " ") \
                .replace(" \t", " ") \
                .replace("	", " ") \
                .replace("  ", " ")

            for escaped_string in self.escaped_strings:
                paragraph = paragraph.replace(escaped_string, "")
            paragraph = paragraph.strip()

            try:
                int(paragraph)
            except ValueError:
                if paragraph != "":
                    intermediate.append(paragraph)
        out = []
        skipped = []
        for i, paragraph in enumerate(intermediate):
            if i in skipped:
                pass
            par, sk = PDFExtractor._check_ending(paragraph, i, intermediate, skipped)
            out.append(par)
            skipped = sk

        intermediate = out
        out = []
        skipped = []
        for i, paragraph in enumerate(reversed(intermediate)):
            if i in skipped:
                pass
            par, sk = PDFExtractor._check_start(paragraph, i, intermediate, skipped)
            out.append(par)
            skipped = sk

        intermediate = reversed(out)
        out = []

        for paragraph in intermediate:
            if len(paragraph.split()) < self._words_threshold:
                continue
            out.append(paragraph)

        for i, paragraph in enumerate(out):
            self.parsed_content.append(self.PageParagraphContent(
                page_num=page_num,
                paragraph_num=i + 1,
                content=paragraph
            ))

    def _filter_content(self):
        self.parsed_content = list(
            filter(
                lambda item: self._min_page_num <= item.page_num <= self._max_page_num,
                self.parsed_content
            )
        )

    @staticmethod
    def _check_ending(paragraph, i, intermediate, skipped):
        if paragraph.endswith("-") and i + 1 < len(intermediate):
            out, skipped = PDFExtractor._check_ending(intermediate[i + 1], i + 1, intermediate, skipped)
            paragraph = paragraph[:-1] + out
            skipped.append(i + 1)

        return paragraph, skipped

    @staticmethod
    def _check_start(paragraph, i, intermediate, skipped):
        if paragraph[0].islower() and i + 1 < len(intermediate):
            out, skipped = PDFExtractor._check_start(intermediate[i + 1], i + 1, intermediate, skipped)
            paragraph = out + " " + paragraph
            skipped.append(i + 1)

        return paragraph, skipped


if __name__ == "__main__":
    p = PDFExtractor()

    for content in p.parsed_content:
        print(f"\n\n\nPage: {content.page_num}, Paragraph: {content.paragraph_num}\n{content.content}")
