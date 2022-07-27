from sop.models.algorithmModel import AlgorithmModel


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
        import_string = AlgorithmModel.objects.get(pk=algo_id).file.path.replace("\\", "/")
        parameters = ""
        for postdata in request.POST:
            if postdata.startswith(str(algo_id)+".parameters"):
                parameters += '"' + postdata.split(":")[1] + '"' + ": " + '"' + request.POST[postdata] + '"' + ",\n"
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
            para += self.getParameters(request, algo_id) + ","
        para = para[:-1]
        if para != "":
            para += "}"
        return para
