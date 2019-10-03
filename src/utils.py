from typing import List, Tuple, Generator
from functools import lru_cache

from elasticsearch import Elasticsearch

from constants import ELASTICSEARCH_URL


@lru_cache(None)
def client():
    return Elasticsearch(ELASTICSEARCH_URL)


def read_vectors(fpath: str) -> Generator[Tuple[str, List[float]], None, None]:
    """Yields (term, vector) pairs."""
    with open(fpath, newline='\n') as f_in:
        for index, line in enumerate(f_in):
            row = line.strip().split(" ")
            yield (row[0], list(map(float, row[1:],)))
