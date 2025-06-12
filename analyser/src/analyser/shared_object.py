from inference import InferenceServerFactory

from data import DataManager

from plugins.cache import Cache


class SharedObject:
    def __init__(
        self,
        config,
        inference_server_manager,
        compute_plugin_manager,
        indexes,
    ):
        self.inference_server_manager = inference_server_manager
        self.compute_plugin_manager = compute_plugin_manager
        self.indexes = indexes

        self.config = config
