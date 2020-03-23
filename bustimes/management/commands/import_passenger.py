"""Import timetable data "fresh from the cow"
"""

import logging
import zipfile
from requests_html import HTMLSession
from django.core.management.base import BaseCommand
from django.utils import timezone
from busstops.models import DataSource, Service
from .import_gtfs import download_if_modified
from .import_transxchange import Command as TransXChangeCommand
from ...models import Route


logger = logging.getLogger(__name__)


sources = (
    # ('Borders Buses', 'https://www.bordersbuses.co.uk/open-data', 'S'),
    ('Reading Buses', 'https://www.reading-buses.co.uk/open-data', 'SE', {
        'RB': 'RBUS',
        'GLRB': 'GLRB'
    }),
)


class Command(BaseCommand):
    def handle(self, *args, **options):

        session = HTMLSession()
        command = TransXChangeCommand()
        command.calendar_cache = {}
        command.undefined_holidays = set()
        command.notes = {}
        command.corrections = {}

        for name, url, region_id, operators in sources:
            command.source, _ = DataSource.objects.get_or_create({'url': url}, name=name)
            command.source.datetime = timezone.now()
            command.operators = operators
            command.region_id = region_id
            command.service_descriptions = {}
            command.service_codes = set()

            response = session.get(url)
            for element in response.html.find():
                if element.tag == 'h3':
                    heading = element.text
                elif element.tag == 'a':
                    url = element.attrs['href']
                    if '/txc/' in url:
                        url = element.attrs['href']
                        path = url.split('/')[-1]
                        modified = download_if_modified(path, url)
                        print(url, heading, modified)

                        # the file might be plain XML, or a zipped archive - we just don't know yet
                        try:
                            with open(path) as open_file:
                                command.handle_file(open_file, path)
                        except UnicodeDecodeError:
                            with zipfile.ZipFile(path) as archive:
                                for filename in archive.namelist():
                                    with archive.open(filename) as open_file:
                                        command.handle_file(open_file, filename)
                        break

            routes = Route.objects.filter(service__operator__in=operators.values())
            print(routes.exclude(source=command.source).delete())
            print(command.source.route_set.filter(service__current=False).delete())
            services = Service.objects.filter(operator__in=operators.values(), current=True)
            print(services.exclude(service_code__in=command.service_codes).update(current=False))