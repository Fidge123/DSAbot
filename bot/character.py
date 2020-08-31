import re


class Character:
    def __init__(self, newUserId):
        self.user = newUserId
        self.replace_lib = {}

    def addReplace(self, replace_from, replace_to):

        return_string = ""
        replace_from = replace_from.upper()
        replace_to = replace_to.upper()

        if replace_from in self.replace_lib:
            return_string += "Replacing previous define "
        self.replace_lib[replace_from] = replace_to
        return_string += "Defined {} to {}".format(replace_from, replace_to)
        self.persistSelf()

        return return_string

    def removeReplace(self, remove_key):
        remove_key = remove_key.upper()

        if remove_key in self.replace_lib:
            del self.replace_lib[remove_key]
            return_string = "Succesfully removed {}".format(str(remove_key))
        else:
            return_string = "{} not found in your defines".format(str(remove_key))
        self.persistSelf()
        return return_string

    def persistSelf(self):
        return

    def modifyMessage(self, raw_message):
        replace = True
        loops = 0

        while loops < 5 and replace:
            replace = False

            for key, value in self.replace_lib.items():
                pattern = r"\b{}\b".format(key)

                if re.search(pattern, raw_message):
                    raw_message = re.sub(pattern, value, raw_message)
                    replace = True

        if loops >= 5:
            return "Recursion Depth too great, fix your defines"
        else:
            return raw_message

    def readAttributes(self):
        return

    def preParseMessage(self, message):

        matcher_define = re.compile(
            r"""^!?save( ((?P<key>\w+) (?P<value>\w+)))""", re.VERBOSE | re.I,
        )
        matcher_attr = re.compile(
            r"""!?saveAttr ?(?P<num>(\d+\b,? ?){8})""", re.VERBOSE | re.I,
        )

        if matcher_define.search(message):
            self.addReplace()  # todo

        if matcher_attr.search(message):
            self.addReplace()  # todo

    def purgeDefines(self):
        self.replace_lib = {}
        return

    def loadBaseSkills(self):
        return
