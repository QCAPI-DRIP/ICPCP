# coding: utf-8

from __future__ import absolute_import

import json

from flask import json
from six import BytesIO

from swagger_server.test import BaseTestCase

import requests
import time
import os

# You can alternatively define these in travis.yml as env vars or arguments
BASE_URL = 'https://view.commonwl.org'
WORKFLOW_PATH = '/workflows/workflow.cwl'


# Whole workflow URL on github
workflowURL = 'https://bitbucket.org/markrobinson96/workflows.git'

# Headers
HEADERS = {
    'user-agent': 'my-app/0.0.1',
    'accept': 'application/json'
}


class TestService(BaseTestCase):



    def test_add_new_workflow(self):
        response = requests.post(BASE_URL + '/workflows',
                                    data={'url': workflowURL,'branch':'master','path': '/workflows/make-to-cwl/dna.cwl'},
                                    headers=HEADERS)
        self.assertStatus(response, 202, 'Workflow accepted')
        self.assertIsNotNone(response.headers)
        self.assertIsNotNone(response.headers['Location'])
        location = response.headers['Location']


    def test_get_workflow(self):
        response = requests.get(BASE_URL +
                                '/workflows/github.com/mnneveau/cancer-genomics-workflow/blob/master/pindel/pindel_cat.cwl',
                                headers=HEADERS)

        self.assert200(response,
                       'Response body is : ' + response.content.decode('utf-8'))
        content_dict = json.loads(response.content.decode('utf-8'))

        print(content_dict)




if __name__ == '__main__':
    import unittest
    unittest.main()
