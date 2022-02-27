class StatusTracker():
    
    def __init__(self,instance,status_attr,status_values,commit=True):
        self.instance = instance
        self.status_attr = status_attr
        self.commit = commit
        for status in status_values:
            setattr(self,status[0],status[0])

    @property
    def status(self):
        return getattr(self.instance,self.status_attr)
    @status.setter
    def status(self,value):
        setattr(self.instance,self.status_attr,value)
        if self.commit:
            self.instance.save()