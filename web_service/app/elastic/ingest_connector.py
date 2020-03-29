import base64

from elasticsearch.client import IngestClient
from flask import current_app

from app import db, KnowledgePdfContent


class IngestConnector:
    def __init__(
            self,
            pipeline_id: str = "pdf_content",
            field: str = "data",
            pipeline_description: str = "Extracting info from pdf content"
    ):
        self.pipeline_id: str = pipeline_id
        self.index_name: str = pipeline_id + "_index"
        self.field: str = field
        self.pipeline_description: str = pipeline_description

        self.ingest_client = IngestClient(current_app.elasticsearch)

    def create_pipeline(self):
        self.ingest_client.put_pipeline(id=self.pipeline_id, body={
            'description': self.pipeline_description,
            'processors': [
                {"attachment": {"field": self.field}}
            ]
        })

    def delete_pipeline(self):
        self.ingest_client.delete_pipeline(id=self.pipeline_id)

    def get_pipeline(self):
        return self.ingest_client.get_pipeline(id=self.pipeline_id)

    def add_to_index(
            self,
            id_: int,
            content: str,
            content_page: int,
            content_paragraph: int
    ):
        current_app.elasticsearch.index(
            index=self.index_name,
            id=id_,
            pipeline=self.pipeline_id,
            body={
                self.field: base64.b64encode(content.encode("utf-8")).decode("utf-8"),
                "content_page": content_page,
                "content_paragraph": content_paragraph,
            }
        )

    def remove_from_index(self, id_: int):
        current_app.elasticsearch.delete(index=self.index_name, id=id_)

    def search(self, query: str):
        search = current_app.elasticsearch.search(
            index=self.index_name,
            body={
                "query": {"match": {"attachment.content": query}}
            }
        )

        ids = [int(hit['_id']) for hit in search['hits']['hits']]

        when = []
        for i in range(len(ids)):
            when.append((ids[i], i))
        return KnowledgePdfContent.query.filter(
            KnowledgePdfContent.id.in_(ids)
        ).order_by(
            db.case(when, value=KnowledgePdfContent.id)
        )[0]
