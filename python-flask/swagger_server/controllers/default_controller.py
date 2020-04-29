import connexion
import six

from swagger_server.models.cwl_git import CWLGit  # noqa: E501
from swagger_server import util


def add_workflow(body):  # noqa: E501
    """add a cwl workflow

     # noqa: E501

    :param body: Workflow git request
    :type body: dict | bytes

    :rtype: None
    """
    if connexion.request.is_json:
        body = CWLGit.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'
