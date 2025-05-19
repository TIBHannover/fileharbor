import os
import re
import sys
import logging
import importlib
from typing import List, Dict

from analyser.utils.plugin.manager import Manager
from analyser.utils.plugin.plugin import Plugin


class IndexerPluginManager(Manager):
    _indexer_plugins = {}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.find()
        self.plugin_list = self.init_plugins()

    @classmethod
    def export(cls, name):
        def export_helper(plugin):
            cls._indexer_plugins[name] = plugin
            return plugin

        return export_helper

    def plugins(self):
        return self._indexer_plugins

    def find(
        self, path=os.path.join(os.path.abspath(os.path.dirname(__file__)), "indexer")
    ):
        file_re = re.compile(r"(.+?)\.py$")

        for pl in os.listdir(path):
            match = re.match(file_re, pl)

            if match:
                a = importlib.import_module(
                    "analyser.plugins.indexer.{}".format(match.group(1))
                )
                function_dir = dir(a)

                if "register" in function_dir:
                    a.register(self)

    def get_collection_indexes(self, name: str = None):
        if name is None:
            name = "default"

        # TODO add lock here
        logging.info(f"[IndexerPluginManager]: get_collection_indexes")

        for plugin in self.plugin_list:
            plugin = plugin["plugin"]
            logging.info(f"[IndexerPluginManager]: {plugin.name}")

            return plugin.get_collection_indexes(
                name=name,
            )

    def create_collection(self, name, indexes: List[Dict]):

        # TODO add lock here
        logging.info(f"[IndexerPluginManager]: create_collection")

        for plugin in self.plugin_list:
            plugin = plugin["plugin"]
            logging.info(f"[IndexerPluginManager]: {plugin.name}")

            plugin.create_collection(
                name=name,
                indexes=indexes,
            )

    def delete_collection(self, name):

        # TODO delete lock here
        logging.info(f"[IndexerPluginManager]: delete_collection")

        for plugin in self.plugin_list:
            plugin = plugin["plugin"]
            logging.info(f"[IndexerPluginManager]: {plugin.name}")

            plugin.delete_collection(
                name=name,
            )

    def add_points(self, collection_name, points: List[Dict]):
        # TODO add lock here
        logging.info(f"[QDrantIndexer]: add_points")

        for plugin in self.plugin_list:
            plugin = plugin["plugin"]
            logging.info(f"[IndexerPluginManager]: {plugin.name}")

            plugin.add_points(collection_name=collection_name, points=points)

    def indexing(
        self,
        index_entries=None,
        collections=None,
        rebuild=False,
        plugins=None,
        configs=None,
    ):
        # TODO add lock here
        logging.info(f"[IndexerPluginManager]: indexing")
        logging.info(f"[IndexerPluginManager]: {len(self.plugin_list)} {collections}")

        for plugin in self.plugin_list:
            plugin = plugin["plugin"]
            logging.info(f"[IndexerPluginManager]: {plugin.name}")

            plugin.indexing(
                index_entries=index_entries,
                rebuild=rebuild,
                collections=collections,
            )

    def search(
        self,
        queries,
        filters,
        size=100,
    ):
        logging.error(f"INDEX {queries}")
        result_list = []

        for plugin in self.plugin_list:
            plugin = plugin["plugin"]
            entries = plugin.search(
                queries=queries,
                filters=filters,
                size=size,
            )

            result_list.extend(entries)

        return result_list

    def delete(
        self,
        collections=None,
    ):
        # TODO add lock here
        logging.info(f"[IndexerPluginManager]: delete")
        logging.info(f"[IndexerPluginManager]: {len(self.plugin_list)} {collections}")

        for plugin in self.plugin_list:
            plugin = plugin["plugin"]
            logging.info(f"[IndexerPluginManager]: {plugin.name}")

            plugin.delete(
                collections=collections,
            )


class IndexerPlugin(Plugin):
    _type = "indexer"

    def __init__(self, **kwargs):
        super(IndexerPlugin, self).__init__(**kwargs)

    def indexing(self, train_entries, index_entries):
        pass

    def search(self, queries, size=100):
        pass
