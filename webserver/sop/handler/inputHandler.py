from django.contrib import messages


class InputHandler():
    def checkInput(self, request):
        """ Checks the input that is needed to create a new experiment

        Returns:
            boolean: if the input is correct -> True
        """
        value = True
        if request.POST.get("name") == "":
            messages.warning(request, "The name field needs to be filled in")
            value = False
        checkInputAndInteger = ["minDimension", "maxDimension", "seed", "repetitions", "numberSubspaces"]
        for input in checkInputAndInteger:
            if request.POST.get(input) is not None:
                if request.POST.get(input) == "":
                    messages.warning(request, "You need to specify the " + input)
                    value = False
                else:
                    try:
                        if int(request.POST.get(input)) <= 0:
                            messages.warning(request, "Your " + input + " needs to be bigger than 0")
                            value = False
                    except ValueError:
                        messages.warning(request, "Your " + input + " needs to be a integer")
                        value = False
        try:
            if int(request.POST.get("minDimension", 0)) > int(request.POST.get("maxDimension", 1)):
                messages.warning(request, "Your min dimension can not be bigger than the max dimension")
                value = False
        except:
            pass
        try:
            if int(request.POST.get("repetitions")) > 100:
                messages.warning(request, "The repetitions are maxed at 100")
                value = False
        except ValueError:
            pass
        except TypeError:
            pass
        return value
