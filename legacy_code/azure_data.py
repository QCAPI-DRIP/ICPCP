import requests
from legacy_code.Errors.api_error import APIError
import os
from azure.cli.core import get_default_cli

def request_data(message, key):
    resp = requests.get(message, headers={'Authorization': '{}'.format(key)})
    if resp.status_code != 200:
        raise APIError(resp.text)

    return resp.json()


def get_azure_data(cli_input):
    #taken from: https://stackoverflow.com/questions/51546073/how-to-run-azure-cli-commands-using-python
    args = cli_input.split()
    cli = get_default_cli()
    cli.invoke(args)
    if cli.result.result:
        return cli.result.result
    elif cli.result.error:
        raise cli.result.error
    return True


def extract_servers(data):
    """Extract relevant server info from azure data"""

    pass

if __name__ == '__main__':
    # Get available vms based on location: https://docs.microsoft.com/en-gb/rest/api/compute/virtualmachinesizes/list#code-try-0
    # Get available vms based on subscription: https://docs.microsoft.com/en-us/rest/api/compute/resourceskus/list
    subscription_id = os.environ['AZURE_SUBSCRIPTION_ID']
    key = os.environ['AZURE_SECRET_KEY']
    data = request_data(
        'https://management.azure.com/subscriptions/{}/providers/Microsoft.Compute/locations/westeurope/vmSizes?api-version=2019-12-01'.format(
            subscription_id), key)
    print(data)


