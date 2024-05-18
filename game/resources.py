# -*- coding: utf-8 -*-
import abc
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)
logger.debug("importing...")


class AbstractResourceDescription(metaclass=abc.ABCMeta):
    pass


@dataclass
class BaseResource:
    resource_description: AbstractResourceDescription


class AbstractBaseLoader(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def load(self, resource_description: AbstractResourceDescription) -> BaseResource:
        pass


class ResourceLoader:

    def __init__(self):
        self._loader_map = {}  # {res_descr: loader}
        self._resources = {}  # {res_id: resource}

    def configure_loaders(self, loader_map):
        for res_descr_type, res_loader in loader_map.items():
            if not isinstance(res_descr_type, type(AbstractResourceDescription)):
                raise Exception(
                    f"Resource description '{res_descr_type}' should inherit from: {AbstractResourceDescription}")
            if not isinstance(res_loader, AbstractBaseLoader):
                raise Exception(
                    f"loader for type '{res_descr_type}' does not implement AbstractBaseLoader: {type(res_loader)}")
        self._loader_map = loader_map  # {type:loader}

    def load(self, config):
        resources = {}
        for res_id, desc in config.items():
            if not isinstance(desc, AbstractResourceDescription):
                raise Exception(f"Resource description should inherit from '{AbstractResourceDescription}' "
                                f"but does not for resource id '{res_id}'")

            if res_id in self._resources:  # check cache
                resources[res_id] = self._resources[res_id]
                continue

            loader_type = type(desc)
            loader = self._loader_map.get(loader_type, None)
            if loader:
                res = loader.load(desc)
                if res_id in resources:
                    raise Exception(f"Double resource id detected: {res_id}")
                resources[res_id] = res
                self._resources[res_id] = res
            else:
                raise Exception(f"Loader could not be found for type: {loader_type}")
        return resources


logger.debug("imported")
