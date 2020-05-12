import yaml
import networkx as nx
import random as rng

class CwlParser:

    def __init__(self, filelocation):
        self.filelocation = filelocation
        self.g = nx.DiGraph()
        self.tasks = []
        self.node_count = 0;
        self.cwl_to_dag()

    def check_and_add_dependencies(self, steps):
        for task, value in steps.items():
            self.tasks.append(task)
            self.g.add_node(self.node_count, order=self.node_count, name=task, est=-1, eft=-1, lst=-1,
                                        lft=-1)
            self.node_count += 1
            for k, v in value.items():
                if k == 'in':
                    if isinstance(v, list):
                        for i in v:
                            self.add_dependencies(i, task)

                    elif isinstance(v, dict):
                        for k2, v2 in v.items():
                            self.add_dependencies(v2, task)

                    else:
                        self.add_dependencies(v, task)

    def add_dependencies(self, index, task):
        if '/' in index:
            res = index.split('/')
            if res[0] in self.tasks:
                throughput = rng.randrange(0, 5)
                self.g.add_weighted_edges_from([(self.tasks.index(res[0]), self.tasks.index(task), throughput)])
                #self.g.add_weighted_edges_from([(res[0], task, throughput)])

    def cwl_to_dag(self):
        with open(self.filelocation, 'r') as stream:
            try:
                data = yaml.safe_load(stream)
                if '$graph' in data:
                    graph = data['$graph']
                    for i in graph:
                        if i['id'] == 'main':
                            steps = i['steps']
                            self.check_and_add_dependencies(steps, self.g)

                else:
                    if 'steps' in data:
                        steps = data['steps']
                        self.check_and_add_dependencies(steps)

                    # raise ValueError('Invalid workflow, $graph is missing')

            except yaml.YAMLError as exc:
                print(exc)
