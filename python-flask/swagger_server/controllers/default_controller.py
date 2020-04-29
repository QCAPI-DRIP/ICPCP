import connexion
import six

from swagger_server.models.tosca_template import ToscaTemplate  # noqa: E501
from swagger_server import util


def get_tosca_plan(git_url, path, branch=None):  # noqa: E501
    """get workflow plan as tosca

    Returns a single pet # noqa: E501

    :param git_url: cwl git url
    :type git_url: str
    :param path: the git path.
    :type path: str
    :param branch: the git branch. default is mater
    :type branch: str

    :rtype: ToscaTemplate
    """
    return 'do some magic!'
