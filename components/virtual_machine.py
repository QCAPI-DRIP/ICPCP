class VirtualMachine(object):
    def __init__(self, id, num_cpus, mem_size, disk_size):
        self.id = id
        self.num_cpus = num_cpus
        self.mem_size = mem_size
        self.disk_size = disk_size
