import base64

import numpy as np

from constants import INDEX_NAME, VECTOR_DIMENSIONS
from utils import client, read_vectors


DBIG_NUMPY_TYPE = np.dtype('>f8')


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
                    "vector_fcs": {
                        "type": "binary",
                        "doc_values": True,
                    },
                    "vector_dense": {
                        "type": "dense_vector",
                        "dims": VECTOR_DIMENSIONS,
                        "doc_values": True,
                    }
                }
            },
        }
    )


def base64_encode_array(arr):
    """Encode float array in base 64 format supported by the Fast Cosine Similarity (FCS) plugin."""
    return base64.b64encode(np.array(arr).astype(DBIG_NUMPY_TYPE)).decode("utf-8")


def load_fcs_vectors(fpath):
    """
    Load vectors from file and return them in FCS-ready format.

    Returns a sequence of {"term": str, "vector": str}, dicts.
    """
    vectors = []
    for term, vec in read_vectors(fpath):
        vectors.append({
            "term": term,
            "vector": base64_encode_array(vec),
        })
    return vectors


def load_dense_vectors(fpath):
    """
    Load vectors from file and return them in Elasticsearch dense vector format (7.3+).

    Returns a sequence of {"term": str, "vector": List[float]}, dicts.
    """
    return [{"term": term, "vector": vec} for term, vec in read_vectors(fpath)]


for entry in load_fcs_vectors("./data/slices/vectors_dim200_num1000.txt"):
    print(entry)


for entry in load_dense_vectors("./data/slices/vectors_dim200_num1000.txt"):
    print(entry)
