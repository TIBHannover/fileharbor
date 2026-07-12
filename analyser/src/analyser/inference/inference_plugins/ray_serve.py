import logging
import requests
from typing import Any, Dict, List, Optional
from ray import serve
import ray
import os
from ray.serve import Application
from pathlib import Path
from analyser.plugins.compute_plugin import ComputePlugin, ComputePluginManager
from analyser.inference import InferenceServer, InferenceServerFactory
from google.protobuf.json_format import MessageToDict, ParseDict, Parse


@serve.deployment
class Deployment:
    def __init__(self, plugin: ComputePlugin) -> None:
        self.plugin = plugin

    async def __call__(self, request) -> Dict[str, str]:
        data = await request.json()

        from interface.common_pb2 import PluginRun

        analyse_request = ParseDict(data["inputs"], PluginRun())

        results = self.plugin(analyse_request)

        return MessageToDict(results)


def app_builder(args) -> Application:
    logging.warning(args)
    return Deployment.options(**args["options"]).bind(args["plugin"])


@InferenceServerFactory.export("RayInferenceServer")
class RayInferenceServer(InferenceServer):
    def __init__(self, config: Dict) -> None:
        super().__init__(config)

    def start(
        self,
        compute_plugin_list: List[ComputePlugin],
        compute_plugin_manager: Optional[ComputePluginManager] = None,
    ) -> None:

        # Clear out the leaking container virtual environment tracker
        os.environ.pop("VIRTUAL_ENV", None)

        app_root = Path("/app")
        local_modules = [
            str(app_root / "analyser"),
            str(app_root / "packages" / "data"),
            str(app_root / "packages" / "interface"),
        ]

        # Heavy patterns to completely strip out of the unzipped working environment
        global_excludes = [
            "*.jsonl",
            "**/.venv",
            "**/__pycache__",
            "frontend/",
            "frontend_vue3/",
            "pyproject.toml",
            "poetry.lock",
        ]

        for compute_plugin in compute_plugin_list:
            plugin_instance_name = compute_plugin.instance_name
            logging.info("CLS" + plugin_instance_name)
            plugin_config = compute_plugin.config

            if "inference" in plugin_config:
                inference_config = plugin_config["inference"]
            else:
                inference_config = dict()

            if "requirements" in inference_config:
                requirements = inference_config["requirements"]
            else:
                requirements = list()

            # Construct the isolated environment specification
            runtime_env = {
                "uv": requirements,
                # "py_modules": local_modules,
                "excludes": global_excludes,
                # Force the Ray worker to completely ignore any inherited VIRTUAL_ENV
                "env_vars": {"VIRTUAL_ENV": ""},
            }
            serve.run(
                app_builder(
                    {
                        "plugin": compute_plugin,
                        "options": {
                            "name": plugin_instance_name,
                            "ray_actor_options": {"runtime_env": runtime_env},
                            "autoscaling_config": {"min_replicas": 0},
                        },
                    }
                ),
                route_prefix=f"/{plugin_instance_name}",
                name=plugin_instance_name,
            )

    def __call__(self, compute_plugin, request):
        from interface import analyser_pb2

        plugin_instance_name = compute_plugin.instance_name

        # found = False
        # for compute_plugin in compute_plugin_manager.plugin_list:
        #     plugin_key = compute_plugin["plugin_key"]

        #     plugin_cls = compute_plugin["plugin_cls"]
        #     plugin_config = compute_plugin["config"]

        #     if plugin == plugin_key:
        #         found = True
        #         break

        # if not found:
        #     logging.error(f"{plugin} not found")
        #     return None
        logging.info(f"http://localhost:8000/{plugin_instance_name}")
        try:
            response = requests.post(
                f"http://localhost:8000/{plugin_instance_name}",
                json={
                    "inputs": MessageToDict(request),
                },
            )
        except Exception as e:
            logging.error(f"{e}")
            return None

        try:
            response_dict = response.json()
        except Exception as e:
            logging.error(f"{response} {e}")
            return None

        try:
            return ParseDict(
                response_dict,
                analyser_pb2.AnalyseReply(),
            )
        except Exception as e:
            logging.error(f"{response} {e}")
            return None
