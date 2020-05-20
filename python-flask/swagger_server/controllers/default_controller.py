import connexion
import six

from swagger_server.models.cloud_preferences import CloudPreferences  # noqa: E501
from swagger_server.models.tosca_template import ToscaTemplate  # noqa: E501
from swagger_server import util


def get_tosca_plan(git_url, performance_file_url=None, deadline_file_url=None, price_file_url=None, cloud_preferences=None):  # noqa: E501
    """get workflow plan as tosca

    Returns a single pet # noqa: E501

    :param git_url: cwl git url
    :type git_url: str
    :param performance_file_url: the location of the  performance file
    :type performance_file_url: str
    :param deadline_file_url: the location of the  deadline file
    :type deadline_file_url: str
    :param price_file_url: the location of the  price file
    :type price_file_url: str
    :param cloud_preferences: the cloud preferences
    :type cloud_preferences: dict | bytes

    :rtype: ToscaTemplate
    """
    if connexion.request.is_json:
        cloud_preferences = .from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'
