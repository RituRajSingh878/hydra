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
from typing import List, Optional, Sequence

from hydra.conf import PluginConf
from hydra.core.config_store import ConfigStore
from hydra.core.utils import JobReturn
from hydra.plugins.step_sweeper import StepSweeper
from hydra.plugins.sweeper import Sweeper


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
    provider=__name__,
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
        # TODO: check if can remove job_results
        self.job_results: Optional[List[Sequence[JobReturn]]] = []
        self.overrides: Optional[Sequence[Sequence[Sequence[str]]]] = None
        self.batch_index = 0

    def initialize_arguments(self, arguments: List[str]) -> None:
        lists = []
        for s in arguments:
            key, value = s.split("=")
            lists.append(["{}={}".format(key, val) for val in value.split(",")])

        all_batches = list(itertools.product(*lists))
        assert self.max_batch_size is None or self.max_batch_size > 0
        if self.max_batch_size is None:
            self.overrides = [all_batches]
        else:
            self.overrides = list(
                Sweeper.split_overrides_to_chunks(all_batches, self.max_batch_size)
            )

    def get_job_batch(self) -> Sequence[Sequence[str]]:
        """
        :return: A list of lists of strings, each inner list is the overrides for a single job
        that should be executed.
        """
        assert self.overrides is not None
        self.batch_index += 1
        return self.overrides[self.batch_index - 1]

    def is_done(self) -> bool:
        assert self.overrides is not None
        return self.batch_index >= len(self.overrides)

    def update_results(self, job_results: Sequence[JobReturn]) -> None:
        assert self.job_results is not None
        self.job_results.append(copy.copy(job_results))
