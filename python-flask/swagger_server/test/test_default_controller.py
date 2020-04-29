# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.cwl_git import CWLGit  # noqa: E501
from swagger_server.models.tosca_template import ToscaTemplate  # noqa: E501
from swagger_server.test import BaseTestCase


class TestDefaultController(BaseTestCase):
    """DefaultController integration test stubs"""

    def test_add_workflow(self):
        """Test case for add_workflow

        add a cwl workflow
        """
        body = CWLGit()
        response = self.client.open(
            '/cwl',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_tosca_plan(self):
        """Test case for get_tosca_plan

        get workflow plan as tosca
        """
        response = self.client.open(
            '/tosca/{cwl_id}'.format(cwl_id='cwl_id_example'),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
