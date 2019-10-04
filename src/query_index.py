import random
import time
from typing import List, Tuple

from constants import INDEX_NAME
from populate_index import load_fcs_vectors, FCS_VECTOR_FIELD, DENSE_VECTOR_FIELD, TERM_FIELD, load_dense_vectors
from utils import client


def query_nearest_vectors_fcs(vector_base64: str) -> List[Tuple[str, float]]:
    """Find nearest terms to a given a vector, returning (term, score) pairs."""
    hits = client().search(
        index=INDEX_NAME,
        body={
            "query": {
                "function_score": {
                    "boost_mode": "replace",
                    "functions": [{
                        "script_score": {
                            "script": {
                                "source": "staysense",
                                "lang": "fast_cosine",
                                "params": {
                                    "field": FCS_VECTOR_FIELD,
                                    "cosine": True,
                                    "encoded_vector": vector_base64
                                }
                            }
                        }
                    }]
                }
            }
        },
        _source=[TERM_FIELD]
    )
    neighbours = list((str(hit["_source"][TERM_FIELD]), float(hit["_score"])) for hit in hits["hits"]["hits"])
    return neighbours


def test_query_fcs(fpath, num_repeats) -> float:
    """Get query run time measurements, with random query vector selection, returning average run time (seconds)."""
    vectors = load_fcs_vectors(fpath)
    t0 = time.time()
    for _ in range(num_repeats):
        vector = random.choice(vectors)
        query_nearest_vectors_fcs(vector["vector"])
    return (time.time() - t0) / num_repeats


def query_nearest_vectors_dense(vector: List[float]) -> List[Tuple[str, float]]:
    """Find nearest terms to a given a vector, returning (term, score) pairs."""

    # note thatelasticsearch must have scores >= 0
    # elastic's `cosineSimilarity` func retunrns in range -1 to 1

    hits = client().search(
        index=INDEX_NAME,
        body={
            "query": {
                "function_score": {
                    "boost_mode": "replace",
                    "functions": [{
                        "script_score": {
                            "script": {
                                "source": f"(cosineSimilarity(params.query_vector, doc['{DENSE_VECTOR_FIELD}']) + 1.0) / 2.0",
                                "params": {"query_vector": vector}
                            }
                        }
                    }]
                }
            }
        },
        _source=[TERM_FIELD]
    )

    # REMOVE ME: alternative way of scoring

    # hits = client().search(
    #     index=INDEX_NAME,
    #     body={
    #         "query": {
    #             "script_score": {
    #                 "query": {"match_all": {}},
    #                 "script": {
    #                     "source": f"(cosineSimilarity(params.query_vector, doc['{DENSE_VECTOR_FIELD}']) + 1.0) / 2.0",
    #                     "params": {"query_vector": vector}
    #                 }
    #             }
    #         }
    #     },
    #     _source=[TERM_FIELD]
    # )

    neighbours = list((str(hit["_source"][TERM_FIELD]), float(hit["_score"])) for hit in hits["hits"]["hits"])
    return neighbours


def test_query_dense(fpath, num_repeats) -> float:
    """Get query run time measurements, with random query vector selection, returning average run time (seconds)."""
    vectors = load_dense_vectors(fpath)
    t0 = time.time()
    for _ in range(num_repeats):
        vector = random.choice(vectors)
        query_nearest_vectors_dense(vector["vector"])
    return (time.time() - t0) / num_repeats
