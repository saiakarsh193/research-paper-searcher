# research-paper-searcher
A simple Python based search engine made for research papers.


## PaperExtractor
`PaperExtractor` is used to download research papers from a particular conference.  
Currently implemented for conferences:
- Interspeech

### Usage
```python
# to download papers
pe = PaperExtractor(conference="Interspeech", year=2023)
# to download with extra meta data (will take much longer)
pe = PaperExtractor(conference="Interspeech", year=2023, deep_extract=True)
```
This will download the data as a list of `ResearchPaper` objects.


## SearchEngine
`SearchEngine` is a simple generic index creator and searcher. It is designed for pages having multiple sections.

### Usage
```python
# to create an engine with required sections and their respective importance weights
se = SearchEngine({'category': 3, 'title': 2})
# to add a page with each of its sections
se.add_page(
    page_id=0,
    page_data={
    'category': "Contrastive language-audio pretraining (CLAP) has become a new paradigm to learn audio concepts with audio-text pairs.",
    'title': "CLAP"
    })
# to search for a section-wise query and get sorted results
se.search({'category': "audio"}, max_results=2)
```


## PaperSearch
`PaperSearch` is used to download research papers, save and retrieve them later, and gives us the ability to search through them. It is built using `PaperExtractor` and `SearchEngine`.

### Usage
```python
# to create a new PaperSearch object to download the data
ps = PaperSearch(conference="Interspeech", year=2023, deep_extract=True)
# to write the data, so that you dont need to download every time
ps._write_papers_to_file("interspeech23_raw.txt")

# to load a PaperSearch object using already downloaded and saved data
ps = PaperSearch(load_path="interspeech23_raw.txt")
# to load from multiple sources
ps = PaperSearch(load_path=["interspeech23_raw.txt", "interspeech22_raw.txt"])

# to search through the papers and get the most relevant results
ps.search(category="speech synthesis", query="learn", max_results=4)
ps.search(title="disorder", query="pathological", max_results=1)
```