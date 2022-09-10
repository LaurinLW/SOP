from modernrpc.core import rpc_method
from sop.models.versionModel import VersionModel
from sop.models.subspaceModel import SubspaceModel
from sop.models.resultModel import ResultModel
from django.core.files.base import File
import os
import shutil


@rpc_method
def receiveProgress(percent, version_id):
    """This rpc method receives a progress percent and saves it to the Version

    Args:
        percent (int): Progress percent
        version_id (int): Identifier of the version

    Returns:
        bool:
    """
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
    """This rpc method receives a error and saves it to the Version

    Args:
        error_message (str): Str that describes the error
        version_id (int): Identifier of the version

    Returns:
        bool:
    """
    try:
        version = VersionModel.objects.get(pk=version_id)
        version.error = error_message
        version.save()
    except VersionModel.DoesNotExist:
        return False
    return True


@rpc_method
def receiveWarning(warning_message, version_id):
    """This rpc method receives a warning and saves it to the Version

    Args:
        warning_message (str): Str that describes the warning
        version_id (int): Identifier of the version

    Returns:
        bool:
    """
    try:
        version = VersionModel.objects.get(pk=version_id)
        version.warning = warning_message
        version.save()
    except VersionModel.DoesNotExist:
        return False
    return True


@rpc_method
def receiveResult(file, version_id):
    """This rpc method receives a result and saves it to the Version

    Args:
        file (str): Str of the file name
        version_id (int): Identifier of the version

    Returns:
        bool:
    """
    try:
        version = VersionModel.objects.get(pk=version_id)
    except VersionModel.DoesNotExist:
        return False
    subspace = SubspaceModel.objects.create(dataset=version.experiment.dataset)
    result = ResultModel()
    result.subspace = subspace
    result.version = version
    result.save()

    experimente_dir = os.path.join(os.path.abspath(os.getcwd()), 'experimente')
    export_path = os.path.join(experimente_dir, str(version.experiment.id) + '.' + str(version.edits) + '.' + str(version.runs), 'export', file)
    result.resultFile.save(file, File(open(export_path)))

    return True
