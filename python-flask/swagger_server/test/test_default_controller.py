# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.tosca_template import ToscaTemplate  # noqa: E501
from swagger_server.test import BaseTestCase


class TestDefaultController(BaseTestCase):
    """DefaultController integration test stubs"""

    def test_get_tosca_plan(self):
        """Test case for get_tosca_plan

        get workflow plan as tosca
        """
        query_string = [('git_url', 'git_url_example'),
                        ('performance_file_url', 'performance_file_url_example'),
                        ('deadline_file_url', 'deadline_file_url_example'),
                        ('price_file_url', 'price_file_url_example')]
        response = self.client.open(
            '/tosca/',
            method='GET',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
