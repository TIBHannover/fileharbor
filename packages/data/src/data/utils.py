import os
import uuid
import logging
import imageio.v3 as iio


def create_data_path(data_dir, data_id, file_ext):
    os.makedirs(os.path.join(data_dir, data_id[0:2], data_id[2:4]), exist_ok=True)
    data_path = os.path.join(
        data_dir, data_id[0:2], data_id[2:4], f"{data_id}.{file_ext}"
    )
    return data_path


def generate_id():
    return uuid.uuid4().hex


def convert_proto_data_to_datamanager(data_manager, data):

    with data_manager.create_data("ListData") as points_list:

        data_id = data.id if data.id else uuid.uuid4().hex

        collection_name = data.collection_name

        with points_list.create_data("ListData") as list_data:
            list_data.id = data_id
            for i, data in enumerate(data.data):
                data_type = data.WhichOneof("data")

                if data_type == "image":
                    with list_data.create_data("ImageData", data.name) as image_data:
                        image_data.ext = data.image.ext

                        image = iio.imread(data.image.content)
                        image_data.save_image(image)

                elif data_type == "bool":
                    with list_data.create_data("BoolData", data.name) as bool_data:
                        bool_data.value = data.bool.value

                elif data_type == "int":
                    with list_data.create_data("IntData", data.name) as int_data:
                        int_data.value = data.int.value

                elif data_type == "float":
                    with list_data.create_data("FloatData", data.name) as float_data:
                        float_data.value = data.float.value

                elif data_type == "text":
                    with list_data.create_data("TextData", data.name) as text_data:
                        text_data.text = data.text.text

                else:
                    logging.warning(
                        f"[Collection::add_points] Data type '{data_type}' is not supported."
                    )
