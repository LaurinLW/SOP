from pydoc import locate

from experiment.run.job import Job
from experiment.run.result import Result
from experiment.supply.parser.parameter_parser import ParameterParser
from experiment.supply.subspace.subspace import Subspace


class JobGenerator:
    """class that generates Jobs"""

    def __init__(self, models: list[str], parser: ParameterParser) -> None:
        """constructor method that creates a JobGenerator

        Args:
            models (list[str]): String list of the import path of all used pyod models
            parser (ParameterParser): Parser that parses a file which contains the parameters of the used models
        """
        self.models: list[str] = models
        self.parser = parser

    def generate(self, subspace: Subspace) -> list[Result]:
        """generates all possible Job pairs of the used models and the given Subspace

        Args:
            subspace (Subspace): Subspace to make Jobs from

        Returns:
            list[Job]: returns a list of the generated Jobs
        """
        job_list: list[Result] = list()

        for i in self.models:
            try:
                klass: object = locate(i)
                # instance: BaseDetector = klass(**self.parser.get_parameters(i))
                job_list.append(Result(Job(subspace=subspace, klass=klass, parameters=self.parser.get_parameters(i))))

            except Exception as e:
                job_list.append(Result(Job(subspace=subspace, klass=None, parameters=None), e=e))

        return job_list
