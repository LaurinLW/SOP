import numpy as np
import experiment.supply.subspace.subspace as subspace
from typing import Optional


class Job:
    """Bundles a model and a subspace for execution. The model may not be trained even after the run stage.
    The scores should be available through get_outlier_scores though. (if no error occured in execution)
    """

    def __init__(
        self,
        subspace: subspace.Subspace = None,
        klass: object = None,
        parameters: dict = None,
    ) -> None:
        """constructor

        Args:
            subspace (Subspace): subspace for model training
            klass (object): object to instantiate
        """
        self._subspace: subspace.Subspace = subspace
        self._klass: object = klass
        self._parameters: dict = parameters
        self._outlier_scores: np.ndarray = None
        self._model = None

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
        return self._parameters

    def get_indexes_after_clean(self) -> np.ndarray:
        return self._subspace.indexes_after_clean

    def get_model_class(self) -> object:
        return self._klass

    def set_model_result(self, model: str, outlierscores: np.ndarray):
        self._model = model
        self._outlier_scores = outlierscores

    def get_model_string(self) -> Optional[str]:
        return self._model
