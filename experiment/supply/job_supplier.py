from typing import TextIO
from pandas import DataFrame
from queue import Queue
from threading import Event, Thread

from experiment.pipelinestage import PipelineStage
from experiment.run.job import Job
from experiment.supply.job_generator import JobGenerator
from experiment.supply.subspace.subspace_generator import SubspaceGenerator


class JobSupplier(PipelineStage):
    """Represents the supply-stage of the pipeline.
    It manages the creation of jobs and moves them over its out-queue to the next Piplelinestage

    Args:
        PipelineStage (_type_): inherits from Pipelinestage which inherits from Thread
    """

    def __init__(
        self,
        number_subspaces: int,
        min_dimension: int,
        max_dimension: int,
        seed: int,
        data: DataFrame,
        models: list[str],
        parameterFile: TextIO,
        out: Queue,
        stop: Event,
    ) -> None:
        """constructor method to create a JobSupplier and start it as a Thread

        Args:
            number_subspaces (int): the wanted number of subspaces
            min_dimension (int): the minimum amount of dimensions in a subspace
            max_dimension (int): the maximum amount of dimensions in a subspace
            seed (int): seed for random numbers
            data (DataFrame): DataFrame to make Subspaces of
            models (list[str]): String list of the import path of all used pyod models
            parameters (JSONField): JSONField of the parameters of the used pyod models
            out (Queue): Queue in which to put Jobs to process
            stop (Event): Event which when triggered stops the Thread JobSupplier
        """

        Thread.__init__(self)
        self.subspace_generator: SubspaceGenerator = SubspaceGenerator(
            number_subspaces, min_dimension, max_dimension, seed, data
        )
        self.__job_generator = JobGenerator(models, parameterFile)
        self.__stop: Event = stop
        self.__out_queue: Queue = out
        self.__jobs_failed_to_add: list[Job] = list()

    def run(self) -> None:
        """method that creates Jobs and puts them into the Queue to be processed when possible"""

        iterator = iter(self.subspace_generator)

        while not self.__stop.is_set():

            try:
                subspace = next(iterator)

            except StopIteration:
                break

            else:
                # maybe implement later to only make new jobs when all old ones were added to the Queue
                job_list: list[Job] = self.__job_generator.generate(subspace)
                job_list = self.__jobs_failed_to_add + job_list
                self.__jobs_failed_to_add.clear()

                for job in job_list:
                    try:
                        self.__out_queue.put(job, True, timeout=self._q_timeout)

                    except Exception:
                        self.__jobs_failed_to_add(job)
                        continue
