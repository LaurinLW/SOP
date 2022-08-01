from modernrpc.core import rpc_method
from sop.models.versionModel import VersionModel
from sop.forms.resultForm import ResultForm
from sop.forms.subspaceForm import SubspaceForm
import os
import shutil


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
        working_dir = os.path.join(os.path.abspath(os.getcwd()), 'experimente', str(version.experiment.id) + '.' + str(version.edits) + '.' + str(version.runs))
        if os.path.exists(working_dir):
            shutil.rmtree(working_dir)
    version.progress = percent
    version.save()
    return True


@rpc_method
def receiveError(error_message, version_id):
    try:
        version = VersionModel.objects.get(pk=version_id)
        version.error = error_message
        version.save()
    except VersionModel.DoesNotExist:
        return False
    return True


@rpc_method
def receiveResult(file, version_id):
    try:
        version = VersionModel.objects.get(pk=version_id)
    except VersionModel.DoesNotExist:
        return False
    subspace = SubspaceForm()
    result = ResultForm()
    subspace.dataset = version.experiment.dataset
    result.resultFile.name = file
    result.subspace = subspace
    result.version = version
    if subspace.is_valid() and result.is_valid():
        subspace.save()
        result.save()
        return True
    return False
