import mock
from django.utils.unittest import TestCase
from django.conf import settings
from adgeletti.models import Size, AdSlot


class SizeTestCase(TestCase):
    def setUp(self):
        self.size = mock.Mock(spec=Size, width=200, height=100)

    def test_stringify(self):
        string = Size.__unicode__(self.size)
        self.assertEqual(string, '200px x 100px')


class AdSlotTestCase(TestCase):
    def setUp(self):
        site = mock.Mock()
        site.name = 'Test site'
        self.slot = mock.Mock(spec=AdSlot, label='LABEL', site=site, ad_unit='UNIT_ID')

    def test_stringify(self):
        string = AdSlot.__unicode__(self.slot)
        self.assertEqual(string, 'LABEL (Test site)')

    def test_ad_unit_id(self):
        string = AdSlot.ad_unit_id(self.slot)
        expected = '%s/%s' % (settings.ADGELETTI_DFP_NETWORK_ID, 'UNIT_ID')
        self.assertEqual(string, expected)

