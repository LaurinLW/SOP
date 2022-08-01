import inspect
from django.apps import AppConfig
import os
import pyod
from django.db.models.signals import post_migrate
import importlib.util
import pyod.models
from django.db.utils import OperationalError


def create_pyod_algorithms(sender, **kwargs):
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
                foo = importlib.util.module_from_spec(spec)
                foo.__package__ = "pyod.models"
                spec.loader.exec_module(foo)
                class_name = ""
                try:
                    algo = getattr(foo, a.replace(".py", "").upper())
                    class_name = a.replace(".py", "").upper()
                except:
                    for method_name in method_name_list:
                        try:
                            algo = getattr(foo, method_name)
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
                    else:
                        algoPara += (f"\"{parameters.args[i]}\": \"{parameters.defaults[i-1]}\",\n")
                algoPara = algoPara[:-2]
                algoPara += "}"
                new_algorithm.name = a.replace(".py", "")
                new_algorithm.parameters = algoPara
                new_algorithm.modul_name = f'sop.models.{a.replace(".py", "")}'
                new_algorithm.class_name = class_name
                print(new_algorithm.file.name)
                new_algorithm.save()
                # Add category


class SopConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sop'

    def ready(self):
        post_migrate.connect(create_pyod_algorithms, sender=self)
