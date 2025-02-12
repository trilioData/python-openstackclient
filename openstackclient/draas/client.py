import logging
from osc_lib import utils

from openstackclient.i18n import _

LOG = logging.getLogger(__name__)

DEFAULT_API_VERSION = '1'
API_VERSION_OPTION = 'os_draas_api_version'
API_NAME = 'failover_group'
API_VERSIONS = {
    '1': 'openstackclient.draas.v1.client.Client',
}

def make_client(instance):
    """Returns a draas service client."""
    LOG.debug('Draas client initialized using OpenStack SDK: %s', instance.sdk_connection.draas)
    return instance.sdk_connection.draas

def build_option_parser(parser):
    """Hook to add global options"""
    parser.add_argument(
        '--os-draas-api-version',
        metavar='<draas-api-version>',
        default=utils.env('OS_DRAAS_API_VERSION', default=DEFAULT_API_VERSION),
        help=_("Draas API version, default=%s (Env: OS_DRAAS_API_VERSION)") % DEFAULT_API_VERSION,
    )
    return parser 
