import pyod.models.base
import numpy as np
import experiment.supply.subspace.subspace as subspace
from typing import Optional


class Job:
    """Bundles a model and a subspace for execution
    """

    def __init__(self, subspace: subspace.Subspace, model: pyod.models.base.BaseDetector) -> None:
        """constructor

        Args:
            subspace (Subspace): subspace for model training
            model (pyod.models.base.BaseDetector): model
        """
        self._subspace = subspace
        self.model = model

    def get_outlier_scores(self) -> Optional[np.ndarray]:
        """returns outlier scores of model training data (subspace data)

        Returns:
            Optional[np.ndarray]: outlier scores, None if model is untrained
        """
        try:
            return self.model.decision_scores_
        except Exception:
            return None

    def get_subspace_dimensions(self) -> list[str]:
        return self._subspace.dimensions

    def get_subspace_data(self) -> np.ndarray:
        return self._subspace.data

    def get_parameters(self) -> dict:
        return self.model.get_params()
