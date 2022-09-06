from django.db import models
from .algorithmModel import AlgorithmModel
from .experimentModel import ExperimentModel
import os
import shutil
import json
import docker
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import pre_delete


EXPERIMENT_IMAGE = "sop-experiment"


class VersionModel(models.Model):
    """ This class is the supclass of the Model-class from Django.
        It contains the essentail fields and data that is stored in the database.
    """
    parameterSettings = models.JSONField(null=True)
    edits = models.IntegerField()
    runs = models.IntegerField()
    seed = models.IntegerField()
    status = models.CharField(max_length=20)
    numberSubspaces = models.IntegerField()
    minDimension = models.IntegerField()
    maxDimension = models.IntegerField()
    progress = models.IntegerField()
    pid = models.CharField(max_length=10, null=True)
    algorithms = models.ManyToManyField(AlgorithmModel)
    experiment = models.ForeignKey(ExperimentModel, on_delete=models.CASCADE)
    error = models.CharField(max_length=100, null=True)

    def start(self) -> bool:
        # prepare working directory for container
        experimente_dir = os.path.join(os.path.abspath(os.getcwd()), 'experimente')
        working_dir = os.path.join(experimente_dir, str(self.experiment.id) + '.' + str(self.edits) + '.' + str(self.runs))

        try:
            if not os.path.exists(experimente_dir):
                os.mkdir(experimente_dir)
            os.mkdir(working_dir)
            os.mkdir(os.path.join(working_dir, 'algorithms'))
            os.mkdir(os.path.join(working_dir, 'algorithms', 'useralgorithms'))

            # copy paramters to correct file
            parameter_file = open(os.path.join(working_dir, 'algorithms', 'parameters.json'), 'w')
            parameter_file.write(self.parameterSettings)
            parameter_file.close()

            # copy algorithms
            paramSettings_py = json.loads(self.parameterSettings)
            for p in paramSettings_py.keys():
                algorithm = AlgorithmModel.objects.get(pk=paramSettings_py[p]["ID"])
                if algorithm.creator is not None:
                    shutil.copy(algorithm.file.path, os.path.join(working_dir, 'algorithms', 'useralgorithms', algorithm.name + '.py'))

            # copy dataset
            shutil.copy(self.experiment.dataset.file.path, os.path.join(working_dir, 'dataset.csv'))
        except Exception:
            shutil.rmtree(working_dir)
            return False
        client = docker.from_env()
        container = client.containers.run(EXPERIMENT_IMAGE,
                                          entrypoint=f'python experimentmain.py -id %d -s %d -d %s -minsd %d -maxsd %d -ns %d -c %s' %
                                          (self.id,
                                           self.seed,
                                           '/experimentconfig',
                                           self.minDimension,
                                           self.maxDimension,
                                           self.numberSubspaces,
                                           settings.RPC_PATH),
                                          network='sop-network',
                                          detach=True,
                                          remove=True,
                                          volumes=[settings.SHARED_EXPERIMENT + '/'
                                                   + str(self.experiment.id) + '.'
                                                   + str(self.edits) + '.'
                                                   + str(self.runs) + ':/experimentconfig'])
        # update version model
        self.pid = container.short_id
        self.status = "running"
        self.experiment.latestVersion = str(self.edits) + "." + str(self.runs)
        self.experiment.latestStatus = "running"
        self.experiment.save()
        self.save()
        return True

    def remove_container(self):
        # remove container with working directory
        try:
            client = docker.from_env()
            container = client.containers.get(self.pid)
            container.kill()
        except:
            pass
        working_dir = os.path.join(os.path.abspath(os.getcwd()), 'experimente', str(self.experiment.id) + '.' + str(self.edits) + '.' + str(self.runs))
        if os.path.exists(working_dir):
            shutil.rmtree(working_dir)


@receiver(pre_delete)
def remove_container_on_delete(sender, **kwargs):
    if 'instance' in kwargs.keys():
        if isinstance(kwargs['instance'], VersionModel):
            kwargs['instance'].remove_container()
