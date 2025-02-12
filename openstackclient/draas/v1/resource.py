from osc_lib.command import command
from osc_lib import utils

class ListResource(command.Lister):
    _description = _("List draas resources")

    def get_parser(self, prog_name):
        parser = super(ListResource, self).get_parser(prog_name)
        return parser

    def take_action(self, parsed_args):
        draas_client = self.app.client_manager.draas
        data = draas_client.resources()
        columns = ('ID', 'Name', 'Status')
        return (columns, (utils.get_item_properties(s, columns) for s in data)) 