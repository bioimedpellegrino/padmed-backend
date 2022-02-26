class AttributeJson():
    def __init__(self,obj,attribute_name):
        import json
        self.obj = obj
        self.attribute_name = attribute_name
        json_attr = getattr(self.obj,self.attribute_name)
        if not json_attr:
            self._content = dict()
        else:
            self._content = json.loads(json_attr)
    @property
    def content(self):
        import json
        json_attr = getattr(self.obj,self.attribute_name)
        if not json_attr:
            self._content = dict()
        else:
            self._content = json.loads(json_attr)
        return self._content
    def __getitem__(self,key):
        return self.content[key]
    def __setitem__(self,key,value):
        import json
        new_json = self.content
        new_json[key] = value
        setattr(self.obj, self.attribute_name, json.dumps(new_json))
    def get(self,key,default=None):
        return self.content.get(key,default)
