import re
from typing import List, Tuple, Generator
from functools import lru_cache

from elasticsearch import Elasticsearch

from constants import ELASTICSEARCH_URL


PARSE_ROW = re.compile("(.+?) (.+)")  # sure-fire way of splitting term from vector


@lru_cache(None)
def client() -> Elasticsearch:
    return Elasticsearch(ELASTICSEARCH_URL, timeout=99999999)


def read_vectors(fpath: str) -> Generator[Tuple[int, str, List[float]], None, None]:
    """Yields (index, term, vector) triples."""

    with open(fpath) as f_in:
        dims = None
        for index, line in enumerate(f_in):
            match = PARSE_ROW.match(line)
            term = match.group(1)
            vector = list(map(float, match.group(2).split(" ")))
            if dims is None:
                dims = len(vector)
            else:
                if dims != len(vector):
                    raise Exception(
                        f"Vector length mismatch. Sniffed length {dims}. "
                        f"Row at index {index} with term {term} has length {len(vector)}. "
                        f"Original row: '{line}'"
                    )
            yield (index, term, vector)
