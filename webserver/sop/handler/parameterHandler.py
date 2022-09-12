from sop.models.algorithmModel import AlgorithmModel
import json
from django.contrib import messages


class ParameterHandler():
    """ This class handels Parameters.
    """

    def getParameters(self, request, algo_id):
        """ Reads the parameters that are in the POST request. Converts them into json format

        Args:
            algo_id (int): the id of an algorithm

        Returns:
            str: returns an string of the parameters in json format
        """
        idalgo = "\"ID\": " + str(algo_id) + ",\n"
        error = False
        algorithm = AlgorithmModel.objects.get(pk=algo_id)
        import_string = f'{algorithm.modul_name}.{algorithm.class_name}'
        parameters = ""
        para = ""
        original_parameters = json.loads(AlgorithmModel.objects.get(pk=algo_id).parameters)
        for postdata in request.POST:
            if postdata.startswith(str(algo_id) + ".parameters"):
                if original_parameters[postdata.split(":")[1]] is not None:
                    original_type = type(original_parameters[postdata.split(":")[1]])
                else:
                    original_type = None
                if original_type == int:
                    try:
                        transformed = int(request.POST[postdata])
                        parameters += f'\"{postdata.split(":")[1]}\": {transformed},\n'
                    except ValueError:
                        error = True
                elif original_type == float:
                    try:
                        transformed = float(request.POST[postdata])
                        parameters += f'\"{postdata.split(":")[1]}\": {transformed},\n'
                    except ValueError:
                        error = True
                elif original_type == bool:
                    try:
                        transformed = True if request.POST[postdata] == "True" or request.POST[postdata] == "true" else False
                        parameters += f'\"{postdata.split(":")[1]}\": %s ,\n' % ('true' if transformed else 'false')
                    except ValueError:
                        error = True
                elif original_type is None:
                    if request.POST[postdata] == "None" or request.POST[postdata] == "none":
                        parameters += f'\"{postdata.split(":")[1]}\": null,\n'
                    else:
                        if request.POST[postdata] == "True" or request.POST[postdata] == "true" or \
                                request.POST[postdata] == "False" or request.POST[postdata] == "false":
                            transformed = True if request.POST[postdata] == "True" or request.POST[postdata] == "true" else False
                            parameters += f'\"{postdata.split(":")[1]}\": %s ,\n' % ('true' if transformed else 'false')
                        else:
                            try:
                                if int(request.POST[postdata]) == float(request.POST[postdata]):
                                    transformed = int(request.POST[postdata])
                                    parameters += f'\"{postdata.split(":")[1]}\": {transformed},\n'
                                else:
                                    transformed = float(request.POST[postdata])
                                    parameters += f'\"{postdata.split(":")[1]}\": {transformed},\n'
                            except:
                                try:
                                    transformed = list(request.POST[postdata])
                                    parameters += f'\"{postdata.split(":")[1]}\": {request.POST[postdata]},\n'
                                except:
                                    parameters += f'\"{postdata.split(":")[1]}\": \"{request.POST[postdata]}\",\n'
                elif original_type is list:
                    parameters += f'\"{postdata.split(":")[1]}\": {request.POST[postdata]},\n'
                else:
                    parameters += f'\"{postdata.split(":")[1]}\": \"{request.POST[postdata]}\",\n'
                if error:
                    messages.warning(request, f"Wrong parameter type for parameter {postdata.split(':')[1]}")
                    error = False
                    para = True
                else:
                    if type(para) != bool:
                        para = '"' + import_string + '"' + ":{\n" + idalgo + parameters[:-2] + "\n}"
        return para

    def getFullJsonString(self, request, version):
        """ Build the finished string in json format

        Args:
            version (VersionModel):

        Returns:
            str: returns an string in json format with all information for the parameter json
        """
        para = "{"
        for algo_id in request.POST.getlist("algorithms"):
            version.algorithms.add(AlgorithmModel.objects.get(pk=algo_id))
            parameters = self.getParameters(request, algo_id)
            if type(parameters) == bool:
                version.algorithms.clear()
                return parameters
            else:
                para += parameters + ","
        para = para[:-1]
        if para != "":
            para += "}"
        return para
