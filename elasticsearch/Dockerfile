FROM elasticsearch:7.0.0

ADD config/shield /usr/share/elasticsearch/config/shield/

RUN bin/elasticsearch-plugin install --batch ingest-attachment
