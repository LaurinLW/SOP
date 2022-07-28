import unittest
from experiment.run.job import Job
from experiment.run.result import Result


class ResultTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.job = Job(None, None)
        self.successful = Result(self.job)
        self.unsuccessful = Result(self.job, Exception())

    @unittest.expectedFailure
    def test_unpack_error(self):
        self.unsuccessful.unpack()

    def test_unpack_successful(self):
        self.assertEqual(self.successful.unpack(), self.job)
