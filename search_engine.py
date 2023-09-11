import re
import math
from typing import Dict, Union, List, Tuple

def make_n_grams(tokens: List[str], max_n_grams: int, sep: str) -> List[str]:
    all_tokens = []
    for n_gram in range(1, max_n_grams + 1):
        for i in range(0, len(tokens), n_gram):
            if i + n_gram <= len(tokens):
                all_tokens.append(sep.join(tokens[i: i + n_gram]))
    return all_tokens

class SearchEngine:
    _STOPWORDS = ["to", "a", "with", "the", "and", "of", "in", "we", "for", "on", "that", "is", "this", "by", "as", "our", "from", "an", "are", "can", "it", "be", "have", "has", "more", "which", "or", "these", "both", "while", "such", "not", "at", "only", "than", "their", "when", "been", "but", "most", "its"]

    def __init__(self, section_weights: Dict[str, Union[int, float]]) -> None:
        self.section_weights = section_weights
        self.ind_to_weight = list(self.section_weights.values())
        self.section_to_ind = {section: ind for ind, section in enumerate(self.section_weights)}
        self.max_n_grams = 2
        self.n_gram_sep = "_"
        self.data: Dict[str, Dict] = {}
        self.total_pages = 0

    def _remove_stopwords(self, tokens: List[str]) -> List[str]:
        return [token for token in tokens if not token in self._STOPWORDS]

    def _clean_and_tokenize(self, text: str) -> List[str]:
        text = re.sub(r"[\-]", " ", text.lower()) # replacing - with space
        text = re.sub(r"[^0-9a-zA-Z\. ]", "", text) # only retaining 0-9a-zA-Z and period and space
        text = re.sub(r" {2,}", " ", text) # removing duplicate spaces
        all_tokens = []
        for sentence in text.split("."):
            tokens = sentence.strip().split()
            tokens = self._remove_stopwords(tokens)
            all_tokens += make_n_grams(tokens=tokens, max_n_grams=self.max_n_grams, sep=self.n_gram_sep)
        return all_tokens
    
    def _counter(self, tokens: List[str]) -> Dict[str, int]:
        unique_tokens = {token: 0 for token in set(tokens)}
        for token in tokens:
            unique_tokens[token] += 1
        return unique_tokens

    def add_page(self, page_id: int, page_data: Dict[str, Union[None, str]]) -> None:
        page_token_data = {}
        for section in page_data:
            assert section in self.section_weights, f"given section {section} was not defined in section_weights"
            if page_data[section] == None:
                continue
            tokens = self._clean_and_tokenize(page_data[section])
            token_counter = self._counter(tokens)
            for token in token_counter:
                if not token in page_token_data:
                    page_token_data[token] = [0] * len(self.section_to_ind)
                page_token_data[token][self.section_to_ind[section]] = token_counter[token]
        for token in page_token_data:
            if not token in self.data:
                self.data[token] = {"TOTAL_COUNT": 0, "DOCUMENT_COUNT": 0}
            self.data[token]["TOTAL_COUNT"] += sum(page_token_data[token])
            self.data[token]["DOCUMENT_COUNT"] += 1
            self.data[token][page_id] = page_token_data[token]
        self.total_pages += 1

    def _score_per_token(self, token: str, idf: Union[float, int], page_scores: List[Union[float, int]], section: Union[None, int]) -> None:
        for page in self.data[token]:
            if page in ["TOTAL_COUNT", "DOCUMENT_COUNT"]:
                continue
            if section == None: # check in all sections
                for section_, tf in enumerate(self.data[token][page]):
                    tf_idf = tf * idf
                    page_scores[page] += tf_idf * self.ind_to_weight[section_]
            else:
                tf = self.data[token][page][section]
                tf_idf = tf * idf
                page_scores[page] += tf_idf * self.ind_to_weight[section]

    def search(self, query: Dict[str, str], max_results: int = 10) -> List[Tuple[Union[float, int], int]]:
        # query = {section: str, "_ALL": str}
        page_scores: List[Union[float, int]] = [0] * self.total_pages
        for section, text in query.items():
            assert section == "_ALL" or section in self.section_weights, f"given section {section} was not defined in section_weights"
            if section == "_ALL":
                section_id = None
            else:
                section_id = self.section_to_ind[section]
            key_tokens = self._clean_and_tokenize(text)
            for token in key_tokens:
                if not token in self.data:
                    continue
                df = self.data[token]["DOCUMENT_COUNT"]
                idf = math.log((1 + self.total_pages) / (1 + df)) + 1
                self._score_per_token(token=token, idf=idf, page_scores=page_scores, section=section_id)
        score_map = [(score, ind) for ind, score in enumerate(page_scores)]
        return sorted(score_map, key=lambda x: x[0], reverse=True)[: max_results]

if __name__ == "__main__":
    se = SearchEngine({'category': 3, 'abstract': 2})
    se.add_page(
        page_id=0,
        page_data={
            'category': "Contrastive language-audio pretraining (CLAP) has become a new paradigm to learn audio concepts with audio-text pairs. CLAP models have shown unprecedented performance as zero-shot classifiers on downstream tasks. To further adapt CLAP with domain-specific knowledge, a popular method is to finetune its audio encoder with available labelled examples. However, this is challenging in low-shot scenarios, as the amount of annotations is limited compared to the model size. In this work, we introduce a Training-efficient (Treff) adapter to rapidly learn with a small set of examples while maintaining the capacity for zero-shot classification. First, we propose a cross-attention linear model (CALM) to map a set of labelled examples and test audio to test labels. Second, we find initialising CALM as a cosine measurement improves our Treff adapter even without training. The Treff adapter beats metric-based methods in few-shot settings and yields competitive results to fully-supervised methods."
        }
    )
    print(se.search(
        query={
            'category': "learn",
            '_ALL': "text"
        },
        max_results=2
    ))
