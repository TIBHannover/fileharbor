import uuid
import logging
from typing import List, Dict

from qdrant_client import QdrantClient
from qdrant_client.http import models

import numpy as np

from analyser.plugins import IndexerPlugin, IndexerPluginManager
from analyser.utils import get_element


@IndexerPluginManager.export("QDrantIndexer")
class QDrantIndexer(IndexerPlugin):
    default_config = {
        "index_type": "cos",
        "host": "localhost",
        "port": 6333,
        "grpc": {"port": 50151, "host": "localhost"},
        # "indexing_size": 105536,
    }

    default_version = 0.1

    def __init__(self, **kwargs):
        super(QDrantIndexer, self).__init__(**kwargs)

        self.port = get_element(self.config, "port")
        if self.port is None:
            self.port = 50151

        self.host = get_element(self.config, "host")
        if self.host is None:
            self.host = "localhost"
        # Read configs
        logging.info(f"[QDrantIndexer] Connection opened")
        self.client = QdrantClient(
            host="qdrant", port=6333, timeout=120, grpc_port=6334, prefer_grpc=False
        )

    def create_collection(self, name, indexes: List[Dict]):

        # TODO add lock here
        logging.info(f"[QDrantIndexer]: create_collection")

        self.client.create_collection(
            collection_name=name,
            vectors_config={
                x["name"]: models.VectorParams(
                    size=x["size"],
                    distance=models.Distance.COSINE,
                    multivector_config=models.MultiVectorConfig(
                        comparator=models.MultiVectorComparator.MAX_SIM
                    ),
                )
                for x in indexes
            },
            quantization_config=models.ScalarQuantization(
                scalar=models.ScalarQuantizationConfig(
                    type=models.ScalarType.INT8,
                    quantile=0.99,
                    always_ram=True,
                ),
            ),
            # optimizers_config=models.OptimizersConfigDiff(
            #     indexing_threshold=1000000000,
            # ),
        )

    def delete_collection(self, name):
        # TODO add lock here
        logging.info(f"[QDrantIndexer]: delete_collection")

        self.client.delete_collection(collection_name=name)

    def add_points(self, collection_name, points: List[Dict]):
        # TODO add lock here
        logging.info(f"[QDrantIndexer]: add_points")
        # for k, v in points[0].get("features", {}).items():
        #     logging.error(f"{k}, {len(v)}, {v}")
        logging.info(f"X: {[x.get("meta",{}) for x in points]}")
        self.client.upsert(
            collection_name=collection_name,
            points=[
                models.PointStruct(
                    id=x.get("id", uuid.uuid4().hex),
                    payload=x.get("meta", {}),
                    vector={k: v for k, v in x.get("features", {}).items()},
                )
                for x in points
            ],
        )

    def search(self, queries, filters, size=100):

        results = []

        must = [
            models.FieldCondition(
                key=f["field"], match=models.MatchValue(value=f["query"])
            )
            for f in filters
            if f["flag"] == "MUST"
        ]
        if len(must) == 0:
            must = None
        should = [
            models.FieldCondition(
                key=f["field"], match=models.MatchValue(value=f["query"])
            )
            for f in filters
            if f["flag"] == "SHOULD"
        ]
        if len(should) == 0:
            should = None
        must_not = [
            models.FieldCondition(
                key=f["field"], match=models.MatchValue(value=f["query"])
            )
            for f in filters
            if f["flag"] == "NOT"
        ]
        if len(must_not) == 0:
            must_not = None

        for q in queries:
            # print(collection_id, flush=True)
            result = self.client.search(
                collection_name="default",
                query_vector=models.NamedVector(
                    name=q["index_name"], vector=q["value"]
                ),
                query_filter=models.Filter(must=must, should=should, must_not=must_not),
                limit=size,
                with_payload=True,
                with_vectors=True,
                # search_params=models.SearchParams(hnsw_ef=512, exact=True),
            )
            results.extend(result)
            # print(f"++++++++++++++++ {result}", flush=True)

        for x in results[:1]:
            print("############", flush=True)
            print(x, flush=True)
            print("############", flush=True)

        results = sorted(results, key=lambda x: -x.score)
        results = [
            {
                "id": uuid.UUID(x.id).hex,
                "meta": x.payload,
                "score": x.score,
                "features": [],
            }
            for x in results
        ]
        for x in results[:2]:
            print(x, flush=True)

        return results

    def delete(self, collections):
        for collection_id in collections:
            self.client.delete_collection(
                collection_name=collection_id + "_342ffe349e8f4addb0c2b49ffe467f27"
            )
