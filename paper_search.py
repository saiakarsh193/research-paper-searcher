from typing import List, Union, Optional
from paper_extractor import PaperExtractor, ResearchPaper, _PAPER_CONFERENCES
from search_engine import SearchEngine

class PaperSearch(PaperExtractor):
    def __init__(self, conference: _PAPER_CONFERENCES = "Interspeech", year: int = 2023, deep_extract: bool = False, load_path: Union[str, List[str]] = "") -> None:
        if load_path != "":
            self.papers: List[ResearchPaper] = []
            if isinstance(load_path, list):
                for path in load_path:
                    self._load_papers_from_file(load_path=path)
            else:
                self._load_papers_from_file(load_path=load_path)
        else:
            super().__init__(conference=conference, year=year, deep_extract=deep_extract)
        self.search_engine = SearchEngine({'category': 5, 'title': 3, 'abstract': 1})
        for ind, paper in enumerate(self.papers):
            self.search_engine.add_page(
                page_id=ind,
                page_data={
                    'category': paper.category,
                    'title': paper.title,
                    'abstract': paper.abstract
                })
    
    def _load_papers_from_file(self, load_path: str) -> None:
        with open(load_path, 'r') as f:
            for line in f.readlines():
                self.papers.append(ResearchPaper.load_from_formatted_string(fstr=line.strip(), sep="<sep>"))

    def _write_papers_to_file(self, write_path: str) -> None:
        with open(write_path, 'w') as f:
            for paper in self.papers:
                f.write(ResearchPaper.get_formatted_string(rp=paper, sep="<sep>") + "\n")

    def search(self, query: str, category: Optional[str] = None, title: Optional[str] = None, max_results: int = 10) -> None:
        search_query = {"_ALL": query}
        if category != None:
            search_query["category"] = category
        if title != None:
            search_query["title"] = title
        score_map = self.search_engine.search(query=search_query, max_results=max_results)
        if score_map[0][0] == 0: # the best result score is 0
            print(f"No results found for query \"{query}\"")
        else:
            print(f"Top results found for query \"{query}\":")
            for ind, (score, page_ind) in enumerate(score_map):
                print(f"{ind}: ({page_ind}) -> {score}")
                print(self.papers[page_ind])

if __name__ == "__main__":
    # ps = PaperSearch(conference="Interspeech", year=2023, deep_extract=False)
    # ps._write_papers_to_file("interspeech23_raw.txt")
    ps = PaperSearch(load_path="interspeech23_raw.txt")
    ps.search(category="speech synthesis", query="learn", max_results=4)
    ps.search(category="Pathological", query="", max_results=4)