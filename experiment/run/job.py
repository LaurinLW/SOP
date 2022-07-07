import pyod
import supply.subspace.subspace as subspace


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
        self._model = model
