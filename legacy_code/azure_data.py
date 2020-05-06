import requests
from legacy_code.Errors.api_error import APIError
import os

def requestData(message, key):
    resp = requests.get(message, headers={'Authorization': '{}'.format(key)})
    if resp.status_code != 200:
        raise APIError(resp.text)

    return resp.json()

def extractServers():
if __name__ == '__main__':
    subscription_id = os.environ['AZURE_SUBSCRIPTION_ID']
    key = os.environ['AZURE_SECRET_KEY']
    data = requestData(
        'https://management.azure.com/subscriptions/{}/providers/Microsoft.Compute/skus?api-version=2019-04-01'.format(
            subscription_id), key)
    #print(data)
