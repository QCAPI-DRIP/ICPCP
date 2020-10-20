from planners.NewVMInstance import NewVMInstance
import yaml


    #[1,2,3,4] [1,2,3]

def naivePlan(dag, combined_input):
    servers = []
    #load input
    with open(combined_input, 'r') as stream:
        data_loaded = yaml.safe_load(stream)
        vm_price = data_loaded[0]["price"]
        number_of_vms = len(vm_price)
        number_of_tasks = len(dag.nodes())

    count = 0
    if number_of_tasks > number_of_vms:
        for node in dag.nodes():
            vm = NewVMInstance(count, vm_price[count], 0, 0, [node])
            count += 1
            if count == number_of_vms - 1:
                count = 0
        return servers

    else:
        for node in dag.nodes():
            vm = NewVMInstance(count, vm_price[count], 0, 0, [node])
            servers.append(vm)
            count += 1
        return servers







