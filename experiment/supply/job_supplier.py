from pandas import DataFrame
from queue import Queue
from threading import Event, Thread

from experiment.pipelinestage import PipelineStage
from experiment.run.job import Job
from experiment.supply.job_generator import JobGenerator
from experiment.supply.parser.parameter_parser_json import JsonParameterParser
from experiment.supply.subspace.subspace_generator import SubspaceGenerator

from experiment.supply.preprocessing.cleaner import Cleaner
from experiment.supply.preprocessing.encoder import Encoder
from experiment.supply.preprocessing.cleaner_drop_nan import DropNaNCleaner
from experiment.supply.preprocessing.encoder_one_hot import EncoderOneHot


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
        parser: JsonParameterParser,
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
            parser (JsonParameterParser): JsonParameterParser with the parameters of the used pyod models
            out (Queue): Queue in which to put Jobs to process
            stop (Event): Event which when triggered stops the Thread JobSupplier
        """

        super().__init__(None, out, stop)
        Thread.__init__(self)
        self.__cleaner: Cleaner = DropNaNCleaner()
        self.__encoder: Encoder = EncoderOneHot()
        self.subspace_generator: SubspaceGenerator = SubspaceGenerator(
            number_subspaces,
            min_dimension,
            max_dimension,
            seed,
            data,
            self.__encoder,
            self.__cleaner,
        )
        self.__job_generator = JobGenerator(models, parser)
        self.__stop: Event = stop
        self.__out_queue: Queue = out
        self.__jobs_failed_to_add: list[Job] = list()

    def run(self) -> None:
        """method that creates Jobs and puts them into the Queue to be processed when possible"""

        iterator = iter(self.subspace_generator)

        while not self.__stop.is_set():

            job_list: list[Job] = list()

            if len(self.__jobs_failed_to_add) == 0:
                try:
                    subspace = next(iterator)

                except StopIteration:
                    break

                job_list: list[Job] = self.__job_generator.generate(subspace)

            job_list: list[Job] = job_list + self.__jobs_failed_to_add
            self.__jobs_failed_to_add.clear()

            for job in job_list:
                try:
                    self.__out_queue.put(job, True, timeout=self._q_timeout)

                except Exception:
                    self.__jobs_failed_to_add.append(job)
                    continue

        self.__stop.wait()
