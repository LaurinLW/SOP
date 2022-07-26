from modernrpc.core import rpc_method
from sop.models.versionModel import VersionModel
from sop.forms.resultForm import ResultForm
from sop.forms.subspaceForm import SubspaceForm


@rpc_method
def receiveProgress(percent, version_id):
    try:
        version = VersionModel.objects.get(pk=version_id)
    except VersionModel.DoesNotExist:
        return False
    if version.status != "running":
        return False
    if percent < 0 or percent > 100:
        return False
    if percent < version.progress:
        return False
    if percent == 100:
        version.status = "finished"
    version.progress = percent
    version.save()
    return True


@rpc_method
def receiveError(error_message, version_id):
    try:
        VersionModel.objects.get(pk=version_id)
    except VersionModel.DoesNotExist:
        return False
    # todo show error to user, maybe new attribute in the database?
    return True


@rpc_method
def receiveResult(file, version_id, pickedColumns):
    try:
        version = VersionModel.objects.get(pk=version_id)
    except VersionModel.DoesNotExist:
        return False
    subspace = SubspaceForm()
    result = ResultForm()
    subspace.pickedColumns = pickedColumns
    subspace.dataset = version.experiment.dataset
    result.resultFile = file
    result.subspace = subspace
    result.version = version
    if subspace.is_valid() and result.is_valid():
        subspace.save()
        result.save()
        return True
    return False
