from __future__ import annotations # for typehint of classname in staticmethod
import typing # for get_args
from typing import Literal, Optional, List, Tuple
import os
import urllib.request 
from bs4 import BeautifulSoup
from tqdm import tqdm

_PAPER_CONFERENCES = Literal[
    "Interspeech",
]

def _load_bs4(link: str) -> BeautifulSoup:
    html = urllib.request.urlopen(link)
    htmlParse = BeautifulSoup(html, 'html.parser')
    return htmlParse

class ResearchPaper:
    def __init__(
            self, 
            title: Optional[str] = None, 
            authors: Optional[List[str]] = None,
            abstract: Optional[str] = None,
            category: Optional[str] = None,
            url: Optional[str] = None,
            pdf_url: Optional[str] = None,
            conference: Optional[str] = None,
            conference_url: Optional[str] = None,
            year: Optional[int] = None
            ) -> None:
        self.title = title
        self.authors = authors
        self.abstract = abstract
        self.category = category
        self.url = url
        self.pdf_url = pdf_url
        self.conference = conference
        self.conference_url = conference_url
        self.year = year
    
    def __repr__(self) -> str:
        max_len = 50
        if isinstance(self.title, str):
            title = self.title[: max_len - 3] + "..." if len(self.title) > max_len else self.title
        else:
            title = ""
        if isinstance(self.authors, list):
            authors = self.authors[0] if len(self.authors) == 1 else f"{self.authors[0]} et al"
        else:
            authors = ""
        if isinstance(self.abstract, str):
            abstract = self.abstract[: max_len - 3] + "..." if len(self.abstract) > max_len else self.abstract
        else:
            abstract = ""
        return f"ResearchPaper({title}|{authors}|{self.category})"
        # return f"ResearchPaper({title}|{authors}|{abstract})"
    
    @staticmethod
    def get_formatted_string(rp: ResearchPaper, sep: str) -> str:
        fauthors = "|".join(rp.authors)
        return f"{rp.title}{sep}{fauthors}{sep}{rp.abstract}{sep}{rp.category}{sep}{rp.url}{sep}{rp.pdf_url}{sep}{rp.conference}{sep}{rp.conference_url}{sep}{rp.year}"
    
    @staticmethod
    def load_from_formatted_string(fstr: str, sep: str) -> ResearchPaper:
        title, fauthors, abstract, category, url, pdf_url, conference, conference_url, year = fstr.split(sep)
        authors = fauthors.split("|")
        return ResearchPaper(
            title=title,
            authors=authors,
            abstract=abstract,
            category=category,
            url=url,
            pdf_url=pdf_url,
            conference=conference,
            conference_url=conference_url,
            year=int(year)
        )

class PaperExtractor:
    def __init__(self, conference: _PAPER_CONFERENCES = "Interspeech", year: int = 2023, deep_extract: bool = True) -> None:
        """
        PaperExtractor is used to download paper data from a particular conference. It return a list of ResearchPaper(s).
        """
        assert conference in list(typing.get_args(_PAPER_CONFERENCES)), f"PaperExtractor not defined for the conference: {conference}"
        assert (2010 <= year and year <= 2023), f"Invalid year given: {year}"
        self.papers: List[ResearchPaper] = []
        print(f"PaperExtractor will start downloading data for the conference: {conference}({year})")
        if conference == "Interspeech":
            self._load_interspeech_papers(year=year, deep_extract=deep_extract)
        print(f"PaperExtractor downloaded and parsed data for the conference: {conference}({year})")
    
    def _load_interspeech_paper_deep_meta(self, paper_link: str) -> Tuple[str, str]:
        paper_abstract = []
        html_bs4 = _load_bs4(paper_link)
        for abst in html_bs4.find_all('p', class_=None):
            paper_abstract.append(abst.contents[0].strip().replace('\n', ' '))
        paper_abstract = " ".join(paper_abstract)
        pdf_link = html_bs4.find('a', class_=None)["href"]
        pdf_link = os.path.join(os.path.dirname(paper_link), pdf_link)
        return paper_abstract, pdf_link

    def _load_interspeech_papers(self, year: int, deep_extract: bool) -> None:
        url = f"https://www.isca-speech.org/archive/interspeech_{year}/index.html"
        html_bs4 = _load_bs4(url)
        for category in tqdm(html_bs4.find_all('div', class_="w3-card w3-round w3-white w3-padding")):
            category_name = category.find('h4').string
            for paper in category.find_all('a', class_="w3-text"):
                paper_title = paper.p.contents[0].strip()
                paper_authors = [author.strip() for author in paper.find('span').string.strip().split(",")]
                paper_link = paper["href"]
                paper_link = os.path.join(os.path.dirname(url), paper_link)
                if deep_extract:
                    paper_abstract, pdf_link = self._load_interspeech_paper_deep_meta(paper_link=paper_link)
                else:
                    paper_abstract, pdf_link = None, None
                self.papers.append(ResearchPaper(
                    title=paper_title,
                    authors=paper_authors,
                    abstract=paper_abstract,
                    category=category_name,
                    url=paper_link,
                    pdf_url=pdf_link,
                    conference="Interspeech",
                    conference_url=url,
                    year=year
                ))

if __name__ == "__main__":
    PaperExtractor("Interspeech")
