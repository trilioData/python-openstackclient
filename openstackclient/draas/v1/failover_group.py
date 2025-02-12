
"""DRaaS v1 Failover Group action implementations"""

import logging

from openstack import utils as sdk_utils
from osc_lib.cli import format_columns
from osc_lib.cli import parseractions
from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils

from openstackclient.common import pagination
from openstackclient.i18n import _

LOG = logging.getLogger(__name__)


_formatters = {
    'member_ids': format_columns.ListColumn,
    'boot_order': format_columns.ListColumn,
}


def _get_failover_group_columns(item, client):
    column_map = {'member_ids': 'members', 'boot_order': 'boot order'}
    hidden_columns = ['metadata', 'location']

    return utils.get_osc_show_columns_for_sdk_resource(
        item, column_map, hidden_columns
    )


class CreateFailoverGroup(command.ShowOne):
    _description = _("Create a new failover group.")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'name',
            metavar='<name>',
            help=_("New failover group name"),
        )
        parser.add_argument(
            'description',
            metavar='<description>',
            help=_("New failover group description"),
        )
        return parser

    def take_action(self, parsed_args):
        draas_client = self.app.client_manager.sdk_connection.draas

        kwargs = {
            'name': parsed_args.name,
            'description': parsed_args.description,
        }

        failover_group = draas_client.create_failover_group(**kwargs)

        display_columns, columns = _get_failover_group_columns(
            failover_group,
            draas_client,
        )
        data = utils.get_item_properties(
            failover_group,
            columns,
            formatters=_formatters,
        )
        return display_columns, data


class DeleteFailoverGroup(command.Command):
    _description = _("Delete existing failover group(s).")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'failover_group',
            metavar='<failover-group>',
            nargs='+',
            help=_("failover group(s) to delete (name or ID)"),
        )
        return parser

    def take_action(self, parsed_args):
        draas_client = self.app.client_manager.sdk_connection.draas
        result = 0
        for group in parsed_args.failover_group:
            try:
                group_obj = draas_client.find_failover_group(
                    group, ignore_missing=False
                )
                draas_client.delete_failover_group(group_obj.id)
            # Catch all exceptions in order to avoid to block the next deleting
            except Exception as e:
                result += 1
                LOG.error(e)

        if result > 0:
            total = len(parsed_args.failover_group)
            msg = _("%(result)s of %(total)s failover groups failed to delete.")
            raise exceptions.CommandError(
                msg % {"result": result, "total": total}
            )


class ListFailoverGroup(command.Lister):
    _description = _("List all failover groups.")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            '--all-projects',
            action='store_true',
            default=False,
            help=_("Display information from all projects (admin only)"),
        )
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help=_("List additional fields in output"),
        )
        # TODO(stephenfin): This should really be a --marker option, but alas
        # the API doesn't support that for some reason
        pagination.add_offset_pagination_option_to_parser(parser)
        return parser

    def take_action(self, parsed_args):
        draas_client = self.app.client_manager.sdk_connection.draas

        kwargs = {}

        if parsed_args.all_projects:
            kwargs['all_projects'] = parsed_args.all_projects

        if parsed_args.offset:
            kwargs['offset'] = parsed_args.offset

        if parsed_args.limit:
            kwargs['limit'] = parsed_args.limit

        data = draas_client.failover_groups(**kwargs)

        columns = (
            'id',
            'name',
            'description',
        )
        column_headers = (
            'ID',
            'description',
        )
        if parsed_args.long:
            columns += (
                'member_ids',
                'boot_order',
                'project_id',
                'user_id',
            )
            column_headers += (
                'Members',
                'Boot Order',
                'Project Id',
                'User Id',
            )

        return (
            column_headers,
            (
                utils.get_item_properties(
                    s,
                    columns,
                    formatters=_formatters,
                )
                for s in data
            ),
        )


class ShowFailoverGroup(command.ShowOne):
    _description = _("Display failover group details.")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'failover_group',
            metavar='<failover-group>',
            help=_("failover group to display (name or ID)"),
        )
        return parser

    def take_action(self, parsed_args):
        draas_client = self.app.client_manager.sdk_connection.draas
        group = draas_client.find_draas_group(
            parsed_args.draas_group, ignore_missing=False
        )
        display_columns, columns = _get_draas_group_columns(
            group,
            draas_client,
        )
        data = utils.get_item_properties(
            group, columns, formatters=_formatters
        )
        return display_columns, data
