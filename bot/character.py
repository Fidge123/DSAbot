class Character

def __init__(self, newUserId):
    self.user = newUserId
    self.replace_lib = {}

def addReplace(self, replace_from, replace_to):

    return_string = ""

    if replace_from in self.replace_lib:
        return_string += "Replacing previous define "
    self.replace_lib[replace_from] = replace_to
    return_string += "Defined {} to {}".format(replace_from, replace_to)
    self.persistSelf()

    return return_string

def removeReplace(self, remove_key):
    if(remove_key in self.replace_lib):
        del self.replace_lib[remove_key]
        return_string = "Succesfully removed {}".format(str(remove_key))
    else:
        return_string = "{} not found in your defines".format(str(remove_key))
    self.persistSelf()
    return return_string

def persistSelf(self):

def modifyMessage(self, raw_message): 

    replace = True
    loops = 0

    while (loops < 5 and replace == True):
        
        replace = False
        
        for key, value in replace_lib:

            raw_message.replace(key, value)



def readAttributes(self):

