import yaml
import networkx as nx


class CwlParser:

    def __init__(self, filelocation):
        self.filelocation = filelocation
        self.g = nx.DiGraph()
        self.tasks = []
        self.cwlToDag()

    def checkAndAddDependency(self, steps):
        for task, value in steps.items():
            self.tasks.append(task)
            self.g.add_node(task)
            for k, v in value.items():
                if k == 'in':
                    if isinstance(v, list):
                        for i in v:
                            self.checkAndAddDependency2(i, task)

                    elif isinstance(v, dict):
                        for k2, v2 in v.items():
                            self.checkAndAddDependency2(v2, task)

                    else:
                        self.checkAndAddDependency2(v, task)

    def checkAndAddDependency2(self, index, task):
        if '/' in index:
            res = index.split('/')
            if res[0] in self.tasks:
                self.g.add_edge(res[0], task)

    def cwlToDag(self):
        with open(self.filelocation, 'r') as stream:
            try:
                data = yaml.safe_load(stream)
                if '$graph' in data:
                    graph = data['$graph']
                    for i in graph:
                        if i['id'] == 'main':
                            steps = i['steps']
                            self.checkAndAddDependency(steps, self.g)
                            # for task, value in steps.items():
                            #     tasks.append(task)
                            #     g.add_node(task)
                            #     # print(task)
                            #     for k, v in value.items():
                            #         if k == 'in':
                            #             for k2, v2 in v.items():
                            #                 if isinstance(v2, list):
                            #                     for j in v2:
                            #                         checkAndAddDependency(j, tasks, task, g)
                            #                 else:
                            #                     checkAndAddDependency(v2, tasks, task, g)

                else:
                    if 'steps' in data:
                        steps = data['steps']
                        self.checkAndAddDependency(steps)
                        # for task, value in steps.items():
                        #     tasks.append(task)
                        #     g.add_node(task)
                        #     for k, v in value.items():
                        #         if k == 'in':
                        #             if isinstance(v, list):
                        #                 for i in v:
                        #                     checkAndAddDependency(i, tasks, task, g)
                        #
                        #             elif isinstance(v, dict):
                        #                 for k2, v2 in v.items():
                        #                     checkAndAddDependency(v2, tasks, task, g)
                        #
                        #             else:
                        #                 checkAndAddDependency(v, tasks, task, g)

                    # raise ValueError('Invalid workflow, $graph is missing')

            except yaml.YAMLError as exc:
                print(exc)
