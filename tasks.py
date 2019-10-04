from invoke import task

import os


ORIGINAL_EMBEDDINGS_URL = "http://nlp.stanford.edu/data/glove.twitter.27B.zip"
ORIGINAL_EMBEDDINGS_ZIP = "data/glove.twitter.27B.zip"
ORIGINAL_EMBEDDINGS_UNZIP_DIR = "data/glove.twitter.27B/"

VECTOR_DIMENSIONS = 200
ORIGINAL_EMBEDDINGS_TXT = f"data/glove.twitter.27B/glove.twitter.27B.{VECTOR_DIMENSIONS}d.txt"

VECTOR_DATA_SLICES_DIR = "data/slices"


@task(name="docker-env")
def docker_env(ctx):
    ctx.run("docker-compose up -d", echo=True)


@task
def dataset(ctx):
    ctx.run(f"curl -L -o '{ORIGINAL_EMBEDDINGS_ZIP}' -C - {ORIGINAL_EMBEDDINGS_URL}", echo=True)
    ctx.run(f"unzip {ORIGINAL_EMBEDDINGS_ZIP} -d {ORIGINAL_EMBEDDINGS_UNZIP_DIR}", echo=True)


def generate_data_slice(ctx, num: int):
    os.makedirs(VECTOR_DATA_SLICES_DIR, exist_ok=True)
    slice_fpath = os.path.join(VECTOR_DATA_SLICES_DIR, f"vectors_dim{VECTOR_DIMENSIONS}_num{num}.txt")
    ctx.run(f"head -n {num} {ORIGINAL_EMBEDDINGS_TXT} > {slice_fpath}", echo=True)


@task
def slices(ctx):
    for exp in range(2, 6 + 1):
        generate_data_slice(ctx, 10**exp)


@task(pre=[dataset, slices])
def prep():
    pass
