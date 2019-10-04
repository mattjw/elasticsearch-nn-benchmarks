import base64
import time
from typing import Optional

from elasticsearch.helpers import streaming_bulk
import numpy as np

from constants import INDEX_NAME, VECTOR_DIMENSIONS
from utils import client, read_vectors


DBIG_NUMPY_TYPE = np.dtype('>f8')

BULK_BATCH_SIZE = 500

TERM_FIELD = "term"
FCS_VECTOR_FIELD = "vector_fcs"
DENSE_VECTOR_FIELD = "vector_dense"


def reset_index():
    if client().indices.exists(INDEX_NAME):
        client().indices.delete(INDEX_NAME)

    client().indices.create(
        INDEX_NAME,
        {
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 1,
            },
            "mappings": {
                "properties": {
                    FCS_VECTOR_FIELD: {
                        "type": "binary",
                        "doc_values": True,
                    },
                    DENSE_VECTOR_FIELD: {
                        "type": "dense_vector",
                        "dims": VECTOR_DIMENSIONS
                    },
                    TERM_FIELD: {
                        "type": "keyword"
                    }
                }
            },
        }
    )


#
# Populate FCS vectors

def base64_encode_array(arr):
    """Encode float array in base 64 format supported by the Fast Cosine Similarity (FCS) plugin."""
    return base64.b64encode(np.array(arr).astype(DBIG_NUMPY_TYPE)).decode("utf-8")


def load_fcs_vectors(fpath):
    """
    Load vectors from file and return them in FCS-ready format.

    Returns a sequence of {"term": str, "vector": str}, dicts.
    """
    vectors = []
    for id, term, vec in read_vectors(fpath):
        vectors.append({
            "id": id,
            "term": term,
            "vector": base64_encode_array(vec),
        })
    return vectors


def load_dense_vectors(fpath):
    """
    Load vectors from file and return them in Elasticsearch dense vector format (7.3+).

    Returns a sequence of {"term": str, "vector": List[float]}, dicts.
    """
    return [{"id": id, "term": term, "vector": vec} for id, term, vec in read_vectors(fpath)]


def populate_vectors(fpath, vector_type: Optional[str] = None, bulk_batch_size=BULK_BATCH_SIZE) -> float:
    """
    Loads vectors and saves them into an Elasticsearch index.

    Returns:
        Total run time for the storage part. Specifically, this does NOT include the time to load from file.
    """
    assert vector_type is not None and vector_type.lower() in ["fcs", "dense"]

    if vector_type.lower() == "dense":
        insertions = [
            {
                "_index": INDEX_NAME, "_type": "_doc", "_id": vec["id"],
                "_source": {TERM_FIELD: vec["term"], DENSE_VECTOR_FIELD: vec["vector"]}
            }
            for vec in load_dense_vectors(fpath)]
    elif vector_type.lower() == "fcs":
        insertions = [
            {
                "_index": INDEX_NAME, "_type": "_doc", "_id": vec["id"],
                "_source": {TERM_FIELD: vec["term"], FCS_VECTOR_FIELD: vec["vector"]}
            }
            for vec in load_fcs_vectors(fpath)]

    reset_index()

    t0 = time.time()
    action_results = list(streaming_bulk(
        client(), actions=insertions, chunk_size=bulk_batch_size, max_retries=0, raise_on_exception=True,
        raise_on_error=True, yield_ok=False))
    client().indices.refresh(INDEX_NAME, )
    dur = time.time() - t0

    assert not action_results
    return dur
