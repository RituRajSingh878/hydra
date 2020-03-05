# Copyright (c) Facebook, Inc. and its affiliates. All Rights Reserved

"""
Basic sweeper can generate cartesian products of multiple input commands, each with a
comma separated list of values.
for example, for:
python foo.py a=1,2,3 b=10,20
Basic Sweeper would generate 6 jobs:
1,10
1,20
2,10
2,20
3,10
3,20
"""
import copy
import itertools
from dataclasses import dataclass
from typing import Optional, Sequence, List

from hydra.conf import PluginConf
from hydra.core.config_store import ConfigStore
from hydra.core.utils import JobReturn
from hydra.plugins.step_sweeper import StepSweeper


@dataclass
class BasicSweeperConf(PluginConf):
    cls: str = "hydra._internal.core_plugins.basic_sweeper.BasicSweeper"

    @dataclass
    class Params:
        max_batch_size: Optional[int] = None

    params: Params = Params()


ConfigStore.instance().store(
    group="hydra/sweeper",
    name="basic",
    node=BasicSweeperConf,
    path="hydra.sweeper",
    provider="hydra",
)


class BasicSweeper(StepSweeper):
    """
    Basic sweeper
    """

    def __init__(self, max_batch_size: Optional[int]) -> None:
        """
        Instantiates
        """
        super(BasicSweeper, self).__init__(max_batch_size=max_batch_size)
        self.job_results: Optional[Sequence[JobReturn]] = None
        self.overrides: Optional[Sequence[Sequence[str]]] = None

    def initialize_arguments(self, arguments: List[str]):
        lists = []
        for s in arguments:
            key, value = s.split("=")
            lists.append(["{}={}".format(key, val) for val in value.split(",")])

        self.overrides: Sequence[Sequence[str]] = list(itertools.product(*lists))

    def get_job_batch(self) -> Sequence[Sequence[str]]:
        """
        :return: A list of lists of strings, each inner list is the overrides for a single job
        that should be executed.
        """
        return self.overrides

    def is_done(self) -> bool:
        # just one batch
        return self.job_results is not None

    def update_results(self, job_results: Sequence[JobReturn]) -> None:
        self.job_results = copy.copy(job_results)
