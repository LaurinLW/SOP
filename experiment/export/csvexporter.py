import experiment.export.exporter as ex
import experiment.progresscontrol as pc
from experiment.run.result import Result
from threading import Event
from queue import Queue
from typing import Optional
import pandas as pd
from experiment.run.job import Job
import os


class CSVExporter(ex.Exporter):
    """ This class is an Exporter implementation that writes the results to disk as a csv file.
    The csv file contains for each subspace its data and for each datapoint the decision score of the models.
    The seperator for the csv file is ','.
    """

    def __init__(self, progress: pc.ProgressControl, in_q: Queue[Result], stop_stage: Event, path: str):
        self._path = path
        self._dataframes: dict[tuple[str], pd.DataFrame] = dict()
        self._next_export_id: int = 0
        super().__init__(progress, in_q, stop_stage)

    def run(self):
        self._progress.register(self)
        next_result: Optional[Result] = None
        export_job: Job
        while not self._stop_stage.is_set():
            if next_result is None:
                try:
                    next_result = self._in_q.get(timeout=self._q_timeout)
                except Exception:
                    # could not get item, try again next iteration
                    pass

            if next_result is not None:
                try:
                    export_job = next_result.unpack()
                except Exception as e:
                    self._progress.update_error(str(next_result.job.model),
                                                next_result.job.get_subspace_dimensions(),
                                                e)
                    continue

                dim_tup = tuple(export_job.get_subspace_dimensions())
                df: pd.DataFrame
                try:
                    df = self._dataframes[dim_tup]
                except KeyError:
                    df = pd.DataFrame(data=export_job.get_subspace_data(),
                                      columns=export_job.get_subspace_dimensions(),
                                      dtype=export_job.get_outlier_scores().dtype)
                    self._dataframes[dim_tup] = df
                    df.insert(0, "index", export_job.get_indexes_after_clean())

                df[str(export_job.model)] = export_job.get_outlier_scores()

                self._progress.update(str(export_job.model), export_job.get_subspace_dimensions())
                next_result = None

    def finalize(self):
        for df in self._dataframes.values():
            df.to_csv(os.path.join(self._path, f"subspace_result{self._next_export_id}.csv"), index=False)
            self._next_export_id += 1

    def finalize_single(self, dims: list[str]) -> str:
        key = tuple(dims)
        export: pd.DataFrame
        try:
            export = self._dataframes[key]
            del self._dataframes[key]
        except KeyError:
            return

        export_file_name = f"subspace_result{self._next_export_id}.csv"

        export.to_csv(os.path.join(self._path, export_file_name), index=False)
        self._next_export_id += 1

        return export_file_name
