import unittest
import experiment.progresscontrol as pc

class ProgressControlTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.experiment = _MockExperiment()
        self.exporter = _MockExporter()
        self.connection = _MockServerConnection()

        self.num_models = 5
        self.num_subspaces = 5
        self.num_subspace_dimensions = 3
        self.subspace_dims = list()
        for i in range(self.num_subspaces):
            subspace = list()
            for j in range(self.num_subspace_dimensions):
                subspace.append(f"dim{i},{j}")
            self.subspace_dims.append(subspace)
        
        self.progress = pc.ProgressControl(self.experiment, self.num_models, self.num_subspaces, self.connection)
        self.progress.register(self.exporter)

    def test_update(self):
        for s in self.subspace_dims:
            for _ in range(self.num_models):
                self.progress.update(s)

        self.assertEqual(self.exporter.finalize_single_count, self.num_subspaces)
        self.assertTrue(self.experiment.called_stop)
        self.assertEqual(self.exporter.finalize_count, 1)
        self.assertEqual(self.connection.received_progress, self.num_models*self.num_subspaces)
        self.assertEqual(self.connection.received_results, self.num_subspaces)
        self.assertEqual(self.connection.received_warnings, 0)

    def test_update_error(self):
        for s in self.subspace_dims:
            for _ in range(self.num_models):
                self.progress.update_error(s, "error")

        self.assertEqual(self.exporter.finalize_single_count, self.num_subspaces)
        self.assertTrue(self.experiment.called_stop)
        self.assertEqual(self.exporter.finalize_count, 1)
        self.assertEqual(self.connection.received_progress, self.num_models*self.num_subspaces)
        self.assertEqual(self.connection.received_results, self.num_subspaces)
        self.assertEqual(self.connection.received_warnings, self.num_models*self.num_subspaces)   


class _MockExperiment():

    def __init__(self) -> None:
        self.called_stop: bool = False

    def stop(self) -> None:
        self.called_stop = True

class _MockExporter():
    def __init__(self) -> None:
        self.finalize_count = 0
        self.finalize_single_count = 0

    def finalize_single(self, dims: list[str]) -> str:
        self.finalize_single_count += 1
        return str(self.finalize_single_count)
    
    def finalize(self) -> None:
        self.finalize_count += 1
    
class _MockServerConnection():
    def __init__(self) -> None:
        self.received_warnings = 0
        self.received_progress = 0
        self.received_results = 0
    
    def send_progress(self, progress: int):
        self.received_progress += 1
    
    def send_error(self, error: str):
        pass

    def send_result(self, name: str):
        self.received_results += 1

    def send_warning(self, warning: str):
        self.received_warnings += 1
    


