from optparse import make_option

from my_django.core.management.base import AppCommand
from my_django.core.management.sql import sql_delete
from my_django.db import connections, DEFAULT_DB_ALIAS

class Command(AppCommand):
    help = "Prints the DROP TABLE SQL statements for the given app name(s)."

    option_list = AppCommand.option_list + (
        make_option('--database', action='store', dest='database',
            default=DEFAULT_DB_ALIAS, help='Nominates a database to print the '
                'SQL for.  Defaults to the "default" database.'),
    )

    output_transaction = True

    def handle_app(self, app, **options):
        return u'\n'.join(sql_delete(app, self.style, connections[options.get('database')])).encode('utf-8')
