import experiment.export.exporter as ex
import experiment.progresscontrol as pc
from experiment.run.result import Result
from threading import Event
from queue import Queue
from typing import Optional
import pandas as pd
from experiment.run.job import Job
import os
import numpy as np


class CSVExporter(ex.Exporter):
    """ This class is an Exporter implementation that writes the results to disk as a csv file.
    The csv file contains for each subspace its data and for each datapoint the decision score of the models.
    The seperator for the csv file is ','.
    """

    def __init__(self, progress: "pc.ProgressControl", in_q: Queue[Result], stop_stage: Event, path: str):
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
                    continue

            if next_result is not None:
                try:
                    export_job = next_result.unpack()
                except Exception as e:
                    self._progress.update_error(next_result.job.get_subspace_dimensions(),
                                                e)

                    export_job = next_result.job
                    df: pd.DataFrame = self._get_dataframe(export_job)

                    column_head: str
                    if export_job.get_model_class() is None:
                        column_head = f"ERROR:{str(e)}"
                    elif export_job.get_model_string is None:
                        column_head = f"ERROR:{e} {export_job.get_model_class()} {export_job.get_parameters()}"
                    else:
                        column_head = f"ERROR:{e} {export_job.get_model_string()}"

                    df[column_head] = np.nan

                    next_result = None
                    continue

                df = self._get_dataframe(export_job)

                df[export_job.get_model_string()] = export_job.get_outlier_scores()

                self._progress.update(export_job.get_subspace_dimensions())
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

    def _get_dataframe(self, export: Job, failed: bool = False) -> pd.DataFrame:
        """Returns dataframe fitting the export job. If that dataframe does not exist it is created.

        Args:
            export (Job): job that will be exported
            failed (bool): should be true if the job failed (result has an exception)

        Returns:
            pd.DataFrame: the fitting dataframe for the job. Is created if it does not already exist.
        """

        dim_tup = tuple(export.get_subspace_dimensions())
        df: pd.DataFrame
        try:
            df = self._dataframes[dim_tup]
        except KeyError:
            df = pd.DataFrame(data=export.get_subspace_data(),
                              columns=export.get_subspace_dimensions(),)
            self._dataframes[dim_tup] = df
            df.insert(0, "index", export.get_indexes_after_clean())

        return df
