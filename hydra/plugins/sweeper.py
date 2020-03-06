# Copyright (c) Facebook, Inc. and its affiliates. All Rights Reserved
"""
Sweeper plugin interface
"""
from abc import abstractmethod
from typing import Any, Iterable, List, Optional, Sequence

from omegaconf import DictConfig

from hydra.core.config_loader import ConfigLoader
from hydra.types import TaskFunction

from .plugin import Plugin


class Sweeper(Plugin):
    """
    An abstract sweeper interface
    Sweeper takes the command line arguments, generates a and launches jobs
    (where each job typically takes a different command line arguments)
    """

    @abstractmethod
    def setup(
        self,
        config: DictConfig,
        config_loader: ConfigLoader,
        task_function: TaskFunction,
    ) -> None:
        raise NotImplementedError()

    @abstractmethod
    def sweep(self, arguments: List[str]) -> Any:
        """
        Execute a sweep
        :param arguments: list of strings describing what this sweeper should do.
        exact structure is determine by the concrete Sweeper class.
        :return: the return objects of all thy launched jobs. structure depends on the Sweeper
        implementation.
        """
        ...

    @staticmethod
    def split_overrides_to_chunks(
        lst: Sequence[Sequence[str]], n: Optional[int]
    ) -> Iterable[Sequence[Sequence[str]]]:
        if n is None or n == -1:
            n = len(lst)
        assert n > 0
        for i in range(0, len(lst), n):
            yield lst[i : i + n]
