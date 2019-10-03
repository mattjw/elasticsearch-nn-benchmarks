FROM docker.elastic.co/elasticsearch/elasticsearch:7.4.0

COPY plugins/ /usr/share/elasticsearch/external/plugins/

RUN ./bin/elasticsearch-plugin list | \
  grep -q fast-cosine-similarity || \
  ./bin/elasticsearch-plugin install --batch \
    file:///usr/share/elasticsearch/external/plugins/fast-cosine-similarity-7.4.0.zip
