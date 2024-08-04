import io

from django.test import SimpleTestCase

from for_runners.gpx_tools.detect_track_type import TrackType, detect_type
from for_runners.tests.fixture_files import get_fixture_path


class DetectTrackTypeSimpleTestCase(SimpleTestCase):
    def test_xml_with_gpx_tag(self):
        self.assertEqual(
            detect_type(io.BytesIO(b'<?xml version="1.0" encoding="UTF-8"?>\r\n<gpx version="1.1"></gpx>')),
            TrackType.GPX,
        )
        self.assertEqual(detect_type(get_fixture_path('garmin_connect_1.gpx')), TrackType.GPX)

    def test_xml_with_kml_tag(self):
        self.assertEqual(
            detect_type(io.BytesIO(b'<?xml version="1.0" encoding="UTF-8"?>\r\n<kml></kml>')),
            TrackType.KML,
        )
        self.assertEqual(detect_type(get_fixture_path('PentaxK1.KML')), TrackType.KML)

    def test_xml_with_unknown_tag(self):
        with self.assertLogs('for_runners'):
            self.assertEqual(detect_type(io.BytesIO(b'<unknown></unknown>')), TrackType.UNKNOWN)
            self.assertEqual(detect_type(io.BytesIO(b'<gpx><invalid></gpx>')), TrackType.UNKNOWN)
            self.assertEqual(detect_type(io.BytesIO(b'')), TrackType.UNKNOWN)
            self.assertEqual(detect_type(io.BytesIO(b'This is not XML')), TrackType.UNKNOWN)
