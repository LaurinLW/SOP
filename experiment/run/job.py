import pyod.models.base
import numpy as np
import experiment.supply.subspace.subspace as subspace
from typing import Optional


class Job:
    """Bundles a model and a subspace for execution. The model may not be trained even after the run stage.
    The scores should be available through get_outlier_scores though. (if no error occured in execution)
    """

    def __init__(self, subspace: subspace.Subspace, model: pyod.models.base.BaseDetector) -> None:
        """constructor

        Args:
            subspace (Subspace): subspace for model training
            model (pyod.models.base.BaseDetector): model
        """
        self._subspace = subspace
        self.model = model
        self._outlier_scores: np.ndarray = None

    def get_outlier_scores(self) -> Optional[np.ndarray]:
        """returns outlier scores of model training data (subspace data)

        Returns:
            Optional[np.ndarray]: outlier scores, None if model is untrained
        """
        try:
            return self.model.decision_scores_
        except Exception:
            return self._outlier_scores

    def get_subspace_dimensions(self) -> list[str]:
        return self._subspace.dimensions

    def get_subspace_data(self) -> np.ndarray:
        return self._subspace.data

    def get_parameters(self) -> dict:
        return self.model.get_params()

    def get_indexes_after_clean(self) -> np.ndarray:
        return self._subspace.indexes_after_clean

    def set_outlier_scores(self, scores: np.ndarray) -> None:
        self._outlier_scores = scores
