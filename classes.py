class function(object):
    def __init__(self):
        pass

class para_list(object):
    def __init__(self):
        self.id_list = []

class para_item(object):
    var_type = "VOID"
    var_name = None
    var_is_ptr = False
    def __init__(self):
        pass

class var_symbol(object):
    var_type = "VOID"
    var_name = None
    var_is_ptr = False
    def __init__(self):
        pass
class symbol(object):
    var_type = ""
    var_name = None
    var_is_ptr = False
    def __init__(self):
        pass

class init_item(object):
    code = ""
    name = ""
    def __init__(self):
        pass

var = var_symbol().__str__
print(type(var).__name__)

'''
p = para_list()
p.id_list.append(["hello", "hello_again"])
print(p.id_list)
'''