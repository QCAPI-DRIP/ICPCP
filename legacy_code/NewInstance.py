class NewInstance(object):
    def __init__(self, vm_type: int, vm_start: int, vm_end: int, pcp: list):
        self.vm_type = vm_type
        self.vm_start = vm_start
        self.vm_end = vm_end
        self.task_list = pcp
        self.cost = 0
        self.properties = {}