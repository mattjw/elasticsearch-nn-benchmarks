from typing import List, Tuple, Generator
from functools import lru_cache

from elasticsearch import Elasticsearch

from constants import ELASTICSEARCH_URL


@lru_cache(None)
def client() -> Elasticsearch:
    return Elasticsearch(ELASTICSEARCH_URL)


def read_vectors(fpath: str) -> Generator[Tuple[int, str, List[float]], None, None]:
    """Yields (index, term, vector) triples."""
    with open(fpath, newline='\n') as f_in:
        for index, line in enumerate(f_in):
            row = line.strip().split(" ")
            yield (index, row[0], list(map(float, row[1:],)))
