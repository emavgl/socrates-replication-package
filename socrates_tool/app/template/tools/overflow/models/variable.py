

class Variable:

    def __init__(self, dic):
        self.name = dic.get('name')

        self.type = dic.get('type')
        if not self.type:
            self.type = dic['typeName']['name']

        self.scope = dic.get('visibility')
        self.stateVariable = dic.get('stateVariable')
        self.storageLocation = dic.get('storageLocation')

    def match(self, properties):

        my_variable = {'name': self.name, 'type': self.type}

        if type(properties) is not dict:
            return False

        for property, value in properties.items():
            if property not in my_variable or my_variable[property] != value:
                return False

        return True