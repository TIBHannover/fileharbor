import logging
import uuid
import copy

from interface import collection_pb2, collection_pb2_grpc
from jobs import IndexingJob
import imageio.v3 as iio
from concurrent import futures


class CollectionServicer(collection_pb2_grpc.CollectionServicer):
    def __init__(self, config, shared_object):
        self.config = config

        self.shared_object = shared_object

        self.add_points_process_pool = futures.ThreadPoolExecutor()
        self.futures = []

    def add(self, request, context):
        logging.info(f"Received analyse request, plugins: {request}")

        self.managers["indexer_manager"].create_collection(
            name=request.name,
            indexes=[{"name": x.name, "size": x.size} for x in request.indexes],
        )

        return collection_pb2.CollectionAddResponse()

    def delete(self, request, context):
        logging.info(f"Received analyse request, plugins: {request}")

        self.shared_object.indexer_plugin_manager.delete_collection(
            collection_name=request.name,
        )

        return collection_pb2.CollectionDeleteResponse()

    def list(self, request, context):
        logging.info(f"Received analyse request, plugins:")

        result = collection_pb2.CollectionListResponse()
        result.names.extend(
            self.shared_object.indexer_plugin_manager.list_collections()
        )

        return result

    def query(self, request, context):
        logging.info(f"Received analyse request, plugins: {request.plugin}")

        return

    def add_points(self, request_iterator, context):
        logging.info(f"Received analyse request, plugins")

        job_id = uuid.uuid4().hex

        collection_name = None
        with self.shared_object.data_manager.create_data("ListData") as points_list:

            for data_point in request_iterator:
                # TODO check if key already exists
                data_id = data_point.id if data_point.id else uuid.uuid4().hex

                collection_name = data_point.collection_name

                with points_list.create_data("ListData") as list_data:
                    list_data.id = data_id
                    for i, data in enumerate(data_point.data):
                        data_type = data.WhichOneof("data")

                        if data_type == "image":
                            with list_data.create_data(
                                "ImageData", data.name
                            ) as image_data:
                                image_data.ext = data.image.ext

                                image = iio.imread(data.image.content)
                                image_data.save_image(image)

                        elif data_type == "bool":
                            with list_data.create_data(
                                "BoolData", data.name
                            ) as bool_data:
                                bool_data.value = data.bool.value

                        elif data_type == "int":
                            with list_data.create_data(
                                "IntData", data.name
                            ) as int_data:
                                int_data.value = data.int.value

                        elif data_type == "float":
                            with list_data.create_data(
                                "FloatData", data.name
                            ) as float_data:
                                float_data.value = data.float.value

                        elif data_type == "text":
                            with list_data.create_data(
                                "TextData", data.name
                            ) as text_data:
                                text_data.text = data.text.text

                        else:
                            logging.warning(
                                f"[Collection::add_points] Data type '{data_type}' is not supported."
                            )

                yield collection_pb2.AddPointsReply(
                    status="ok", id=data_id, indexing_job_id=job_id
                )

        #
        variable = {
            "future": None,
            "id": job_id,
            "points_list": points_list.id,
            "collection_name": collection_name,
        }

        # indexing_job = IndexingJob()
        # indexing_job.init_worker(self.config)
        # indexing_job(copy.deepcopy(variable))

        future = self.add_points_process_pool.submit(
            IndexingJob(shared_object=self.shared_object), copy.deepcopy(variable)
        )
        variable["future"] = future
        self.futures.append(variable)
