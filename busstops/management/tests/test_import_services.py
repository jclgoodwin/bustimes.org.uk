# coding=utf-8
import os
import xml.etree.cElementTree as ET
from django.test import TestCase
from django.contrib.gis.geos import Point
from ...models import Operator, Service, Region, StopPoint
from ..commands import import_services


DIR = os.path.dirname(os.path.abspath(__file__))


class ImportServicesTest(TestCase):
    "Tests for parts of the command that imports services from TNDS"

    command = import_services.Command()

    @classmethod
    def setUpTestData(cls):
        cls.ea = Region.objects.create(pk='EA', name='East Anglia')
        cls.gb = Region.objects.create(pk='GB', name='Großbritannien')
        cls.sc = Region.objects.create(pk='S', name='Scotland')
        cls.london = Region.objects.create(pk='L', name='London')

        cls.fecs = Operator.objects.create(pk='FECS', region_id='EA', name='First in Norfolk & Suffolk')
        cls.megabus = Operator.objects.create(pk='MEGA', region_id='GB', name='Megabus')
        cls.fabd = Operator.objects.create(pk='FABD', region_id='S', name='First Aberdeen')
        cls.blue_triangle = Operator.objects.create(pk='BTRI', region_id='L', name='Blue Triangle')
        cls.blue_triangle_element = ET.fromstring("""
            <txc:Operator xmlns:txc='http://www.transxchange.org.uk/' id='OId_BE'>
                <txc:OperatorCode>BE</txc:OperatorCode>
                <txc:OperatorShortName>BLUE TRIANGLE BUSES LIM</txc:OperatorShortName>
                <txc:OperatorNameOnLicence>BLUE TRIANGLE BUSES LIMITED</txc:OperatorNameOnLicence>
                <txc:TradingName>BLUE TRIANGLE BUSES LIMITED</txc:TradingName>
            </txc:Operator>
        """)

        for atco_code, common_name, indicator, lat, lng in (
                ('639004572', 'Bulls Head', 'adj', -2.5042125060, 53.7423055225),
                ('639004562', 'Markham Road', 'by"', -2.5083672338, 53.7398252112),
                ('639004554', 'Witton Park', 'opp', -2.5108434749, 53.7389877672),
                ('639004552', 'The Griffin', 'adj', -2.4989239373, 53.7425523688)
        ):
            StopPoint.objects.create(
                atco_code=atco_code, locality_centre=False, active=True, common_name=common_name,
                indicator=indicator, latlong=Point(lng, lat, srid=4326)
            )

        cls.do_service('ea_21-13B-B-y08-1', 'EA')
        cls.ea_service = Service.objects.get(pk='ea_21-13B-B-y08')
        cls.do_service('Megabus_Megabus14032016 163144_MEGA_M11A', 'GB', {'MEGAM11A': 'Belgravia - Liverpool'})
        cls.gb_service = Service.objects.get(pk='M11A_MEGA')
        cls.do_service('SVRABBN017', 'S')
        cls.sc_service = Service.objects.get(pk='ABBN017')

    def test_sanitize_description(self):
        testcases = (
            (
                'Bus Station bay 5,Blyth - Grange Road turning circle,Widdrington Station',
                'Blyth - Widdrington Station'
            ),
            (
                '      Bus Station-Std C,Winlaton - Ryton Comprehensive School,Ryton     ',
                'Winlaton - Ryton'
            ),
        )

        for inp, outp in testcases:
            self.assertEqual(self.command.sanitize_description(inp), outp)

    def test_infer_from_filename(self):
        """
        Given a filename string
        get_net() should return a (net, service_code, line_ver) tuple if appropriate,
        or ('', None, None) otherwise.
        """
        data = (
            ('ea_21-2-_-y08-1.xml', ('ea', 'ea_21-2-_-y08', '1')),
            ('ea_21-27-D-y08-1.xml', ('ea', 'ea_21-27-D-y08', '1')),
            ('tfl_52-FL2-_-y08-1.xml', ('tfl', 'tfl_52-FL2-_-y08', '1')),
            ('suf_56-FRY-1-y08-15.xml', ('suf', 'suf_56-FRY-1-y08', '15')),
            ('NATX_330.xml', ('', None, None)),
            ('NE_130_PB2717_21A.xml', ('', None, None)),
            ('SVRABAN007-20150620-9.xml', ('', None, None)),
            ('SVRWLCO021-20121121-13693.xml', ('', None, None)),
            ('National Express_NX_atco_NATX_T61.xml', ('', None, None)),
            ('SnapshotNewportBus_TXC_2015714-0317_NTAO155.xml', ('', None, None)),
            ('ArrivaCymru51S-Rhyl-StBrigid`s-Denbigh1_TXC_2016108-0319_DGAO051S.xml', ('', None, None)),
        )

        for filename, parts in data:
            self.assertEqual(self.command.infer_from_filename(filename), parts)

    def test_get_operator_name(self):
        self.assertEqual(self.command.get_operator_name(self.blue_triangle_element), 'BLUE TRIANGLE BUSES LIMITED')

    def test_get_operator(self):
        element = ET.fromstring("""
            <txc:Operator xmlns:txc="http://www.transxchange.org.uk/" id="OId_RRS">
                <txc:OperatorCode>RRS</txc:OperatorCode>
                <txc:OperatorShortName>Replacement Service</txc:OperatorShortName>
                <txc:OperatorNameOnLicence>Replacement Service</txc:OperatorNameOnLicence>
                <txc:TradingName>Replacement Service</txc:TradingName>
            </txc:Operator>
        """)
        self.assertIsNone(self.command.get_operator(element))

        # test SPECIAL_OPERATOR_TRADINGNAMES
        self.assertEqual(self.blue_triangle, self.command.get_operator(self.blue_triangle_element))

    @classmethod
    def do_service(cls, filename, region, service_descriptions=None):
        filename = '%s.xml' % filename
        path = os.path.join(DIR, 'fixtures', filename)
        if region == 'GB':
            filename = 'NCSD_TXC/%s' % filename
        with open(path) as xml_file:
            cls.command.do_service(xml_file, region, filename, service_descriptions)

    def test_do_service_ea(self):
        service = self.ea_service

        self.assertEqual(str(service), '13B - Turquoise Line - Norwich - Wymondham - Attleborough')
        self.assertEqual(service.line_name, '13B')
        self.assertEqual(service.line_brand, 'Turquoise Line')
        self.assertTrue(service.show_timetable)
        self.assertEqual(service.operator.first(), self.fecs)
        self.assertEqual(
            service.get_traveline_url(),
            'http://www.travelinesoutheast.org.uk/se/XSLT_TTB_REQUEST' +
            '?line=2113B&lineVer=1&net=ea&project=y08&sup=B&command=direct&outputFormat=0'
        )

        res = self.client.get(service.get_absolute_url())
        self.assertEqual(res.context_data['breadcrumb'], [self.ea, self.fecs])
        self.assertContains(res, """
            <tr class="OTH">
                <th>Norwich Brunswick Road</th>
                <td>19:48</td><td>19:48</td><td>22:56</td><td>22:56</td>
                <td>08:57</td><td>09:57</td><td>10:57</td><td>17:57</td>
            </tr>
        """, html=True)

    def test_do_service_ncsd(self):
        service = self.gb_service

        self.assertEqual(str(service), 'M11A - Belgravia - Liverpool')
        self.assertTrue(service.show_timetable)
        self.assertEqual(service.operator.first(), self.megabus)
        self.assertEqual(
            service.get_traveline_url(),
            'http://www.travelinesoutheast.org.uk/se/XSLT_TTB_REQUEST' +
            '?line=11M11A&net=nrc&project=y08&command=direct&outputFormat=0'
        )

        res = self.client.get(service.get_absolute_url())
        self.assertEqual(res.context_data['breadcrumb'], [self.gb, self.megabus])
        self.assertTemplateUsed(res, 'busstops/service_detail.html')
        self.assertContains(res, '<h1>M11A - Belgravia - Liverpool</h1>', html=True)
        self.assertContains(
            res,
            """
            <td colspan="8">Book at <a
            href="https://www.awin1.com/awclick.php?mid=2678&amp;id=242611" rel="nofollow">
            megabus.com</a> or 0900 1600900 (65p/min + network charges)</td>
            """,
            html=True
        )

    def test_do_service_scotland(self):
        service = self.sc_service

        self.assertEqual(str(service), 'N17 - Aberdeen - Dyce')
        self.assertTrue(service.show_timetable)
        self.assertEqual(service.operator.first(), self.fabd)
        self.assertEqual(
            service.get_traveline_url(),
            'http://www.travelinescotland.com/lts/#/timetables?' +
            'timetableId=ABBN017&direction=OUTBOUND&queryDate=&queryTime='
        )
        self.assertEqual(service.geometry.coords, ((
            (53.7423055225, -2.504212506), (53.7398252112, -2.5083672338),
            (53.7389877672, -2.5108434749), (53.7425523688, -2.4989239373)
        ),))

        res = self.client.get(service.get_absolute_url())
        self.assertEqual(res.context_data['breadcrumb'], [self.sc, self.fabd])
        self.assertTemplateUsed(res, 'busstops/service_detail.html')
        self.assertContains(res, '<td colspan="5" rowspan="62">then every 30 minutes until</td>', html=True)

        # Test the fallback version without a timetable (just a list of stops)
        service.show_timetable = False
        service.save()
        res = self.client.get(service.get_absolute_url())
        self.assertContains(res, '<h2>Outbound</h2>')
        self.assertContains(res, """
            <li class="OTH" itemscope itemtype="https://schema.org/BusStop">
                <a href="/stops/639004554">
                    <span itemprop="name">Witton Park (opp)</span>
                    <span itemprop="geo" itemscope itemtype="https://schema.org/GeoCoordinates">
                        <meta itemprop="latitude" content="-2.5108434749" />
                        <meta itemprop="longitude" content="53.7389877672" />
                    </span>
                </a>
            </li>
        """, html=True)
