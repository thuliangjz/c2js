class function(object):
    def __init__(self):
        pass

class para_list(object):
    def __init__(self):
        self.id_list = []

class para_item(object):
    var_type = "VOID"
    var_name = None
    def __init__(self):
        pass

'''
p = para_list()
p.id_list.append(["hello", "hello_again"])
print(p.id_list)
'''