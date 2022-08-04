import inspect
from django.apps import AppConfig
import os
import pyod
from django.db.models.signals import post_migrate
import importlib.util
import pyod.models
from django.db.utils import OperationalError
import json


def create_pyod_algorithms(sender, **kwargs):
    """ Adds the pyod algorithms to the database
    """
    from sop.models import AlgorithmModel
    try:
        AlgorithmModel.objects.all()
    except OperationalError:
        return
    direc = str(pyod.models.__path__).replace("['", "").replace("']", "")
    ignore_list = ["base", "sklearn_base", "suod", "xgbod", "lscp", "gaal_base", "base_dl", "combination"]
    method_name_list = ["AnoGAN", "DeepSVDD", "AutoEncoder", "FeatureBagging", "IForest", "Sampling"]
    for a in os.listdir(direc):
        if not a.startswith("_") and a.replace(".py", "") not in ignore_list:
            if AlgorithmModel.objects.all().filter(creator=None).filter(name=a.replace(".py", "")).exists() is False:
                spec = importlib.util.spec_from_file_location(a.replace(".py", ""), direc + os.path.sep + a)
                methode = importlib.util.module_from_spec(spec)
                methode.__package__ = "pyod.models"
                spec.loader.exec_module(methode)
                class_name = ""
                try:
                    algo = getattr(methode, a.replace(".py", "").upper())
                    class_name = a.replace(".py", "").upper()
                except:
                    for method_name in method_name_list:
                        try:
                            algo = getattr(methode, method_name)
                            class_name = method_name
                        except:
                            pass
                parameters = inspect.getargspec(algo)
                new_algorithm = AlgorithmModel.objects.create(category="")
                algoPara = "{" + f"\"ID\": {new_algorithm.id},\n"
                for i in range(1, len(parameters.args)):
                    default_type = type(parameters.defaults[i - 1])
                    if default_type == int or default_type == float:
                        algoPara += (f"\"{parameters.args[i]}\": {parameters.defaults[i-1]},\n")
                    elif default_type == bool:
                        if bool:
                            algoPara += (f"\"{parameters.args[i]}\": true,\n")
                        else:
                            algoPara += (f"\"{parameters.args[i]}\": false,\n")
                    elif parameters.defaults[i - 1] is None:
                        algoPara += (f"\"{parameters.args[i]}\": null,\n")
                    elif default_type == list:
                        algoPara += (f"\"{parameters.args[i]}\": {parameters.defaults[i-1]},\n")
                    else:
                        default = str(parameters.defaults[i - 1]).split(" at ")[0]
                        if default != str(parameters.defaults[i - 1]):
                            algoPara += (f"\"{parameters.args[i]}\": \"{default}>\",\n")
                        else:
                            algoPara += (f"\"{parameters.args[i]}\": \"{parameters.defaults[i-1]}\",\n")
                algoPara = algoPara[:-2]
                algoPara += "}"
                new_algorithm.name = a.replace(".py", "")
                new_algorithm.parameters = algoPara
                new_algorithm.modul_name = f'pyod.models.{a.replace(".py", "")}'
                new_algorithm.class_name = class_name
                json_file = json.load(open("sop/pyod_algorithms_categories.json"))
                if a.replace(".py", "") in json_file:
                    new_algorithm.category = json_file[a.replace(".py", "")]
                new_algorithm.save()


class SopConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sop'

    def ready(self):
        post_migrate.connect(create_pyod_algorithms, sender=self)
