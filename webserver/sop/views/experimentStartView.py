from django.shortcuts import redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from sop.models import ExperimentModel, VersionModel
from django.db.models import Q
import docker
import os
import shutil
import json

from sop.models.algorithmModel import AlgorithmModel


class ExperimentStartView(View, LoginRequiredMixin):
    """ This class is a subclass of LoginRequiredMixin and View
    """
    EXPERIMENT_IMAGE = "sop-experiment"

    def get(self, request, *args, **kwargs):
        """ This method handels the get request from the User.
            The method start the experiment.

        Returns:
            HttpResponseRedirect: Redirects to the detail view of the experiment
        """
        experiment = ExperimentModel.objects.get(id=kwargs.get("detail_id"))
        version = VersionModel.objects.get(Q(experiment_id=experiment.id) & Q(edits=kwargs.get("edits")) & Q(runs=kwargs.get("runs")))
        if experiment.creator == request.user:
            if version.error is None:

                version.status = "running"
                version.experiment.latestVersion = str(version.edits) + "." + str(version.runs)
                version.experiment.latestStatus = "running"
                version.experiment.save()
                version.save()

                # prepare working directory for container
                experimente_dir = os.path.join(os.path.abspath(os.getcwd()), 'experimente')
                working_dir = os.path.join(experimente_dir, str(experiment.id) + '.' + str(version.edits) + '.' + str(version.runs))

                try:
                    if not os.path.exists(experimente_dir):
                        os.mkdir(experimente_dir)
                    os.mkdir(working_dir)
                    os.mkdir(os.path.join(working_dir, 'algorithms'))
                    os.mkdir(os.path.join(working_dir, 'algorithms', 'useralgorithms'))

                    # copy paramters to correct file
                    parameter_file = open(os.path.join(working_dir, 'algorithms', 'parameters.json'), 'w')
                    parameter_file.write(version.parameterSettings)
                    parameter_file.close()

                    algorithms_file = open(os.path.join(working_dir, 'algorithms', 'algorithms.txt'), 'w')
                    # copy algorithms
                    paramSettings_py = json.loads(version.parameterSettings)
                    for p in paramSettings_py.keys():
                        algorithm = AlgorithmModel.objects.get(pk=paramSettings_py[p]["ID"])
                        if algorithm.creator is not None:
                            shutil.copy(algorithm.file.path, os.path.join(working_dir, 'algorithms', 'useralgorithms', algorithm.name + '.py'))
                        algorithms_file.write(algorithm.name + '\n')

                    # copy dataset
                    shutil.copy(experiment.dataset.file.path, os.path.join(working_dir, 'dataset.csv'))
                except Exception:
                    shutil.rmtree(working_dir)
                    return redirect("/details/" + str(experiment.id) + "/" + str(version.edits) + "." + str(version.runs))

                client = docker.from_env()
                container = client.containers.run(ExperimentStartView.EXPERIMENT_IMAGE,
                                                  command=f'python experimentstart.py -id %d -s %d -d %s -minsd %d -maxsd %d -ns %d' %
                                                  (version.id,
                                                   version.seed,
                                                   '/experimentconfig',
                                                   version.minDimension,
                                                   version.maxDimension,
                                                   version.numberSubspaces),
                                                  detach=True,
                                                  auto_remove=True,
                                                  volumes={working_dir: {'bind': '/experimentconfig', 'mode': 'rw'}})

                version.pid = container.short_id
                version.save()

            return redirect("/details/" + str(experiment.id) + "/" + str(version.edits) + "." + str(version.runs))
