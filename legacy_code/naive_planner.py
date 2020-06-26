import os
import sys
import re
import random
import networkx as nx
import numpy as np
from legacy_code.NewInstance import NewInstance as instance
import yaml

class NaivePlanner:
    [1,2,3] [1,2,3,4]
    def planTasks(self, dag, combined_input):
        #load input
        with open(combined_input, 'r') as stream:
            data_loaded = yaml.safe_load(stream)
            self.vm_price = data_loaded[0]["price"]
            perf_data = data_loaded[1]["performance"]
            self.deadline = data_loaded[2]["deadline"]
            l = []
            for key, value in perf_data.items():
                l.append(value)


        num_tasks = len(dag.nodes())
        for node in dag.nodes()




