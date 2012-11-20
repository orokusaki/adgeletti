import json
import mock
from adgeletti.models import Size, AdSlot, AdPosition
from adgeletti.templatetags import adgeletti_tags as tags
from django import template
from django.contrib.sites.models import Site
from django.utils.unittest import TestCase


class ErrorTestCase(TestCase):
    @mock.patch('adgeletti.templatetags.adgeletti_tags.escape')
    def test_error_strings(self, escape):
        escape.return_value = 'BAR'
        error = tags.error('FOO')
        escape.assert_called_with('FOO')
        self.assertEqual(error, '<!-- BAR -->\n')


class ParseAdTestCase(TestCase):
    def test_parse_ad(self):
        token = mock.Mock()
        token.split_contents = mock.Mock(return_value=['ad', 'SLOT', 'BREAKPOINT'])
        node = tags.parse_ad(None, token)
        self.assertEqual(node.slot, 'SLOT')
        self.assertListEqual(node.breakpoints, ['BREAKPOINT'])

    def test_parse_ad_bad_args(self):
        token = mock.Mock()
        token.split_contents = mock.Mock(return_value=['ad', 'SLOT'])
        with self.assertRaises(template.TemplateSyntaxError) as exc:
            tags.parse_ad(None, token)
        self.assertEqual(str(exc.exception), u'usage: {% ad SLOT BREAKPOINT [BREAKPOINT ...] %}')


class AdNodeTestCase(TestCase):
    def setUp(self):
        self.node = tags.AdNode('SLOT', ['A', 'B'])

    def test_clean_value(self):
        invalid_chars = ['!', '^', ' ', '+', '=', '\n']
        for char in invalid_chars:
            s = tags.AdNode.clean_value(char)
            self.assertEqual(s, tags.AdNode._replace)

        valid_chars = ['a', 'A', '1', '9', '_', '-']
        for char in valid_chars:
            s = tags.AdNode.clean_value(char)
            self.assertEquals(s, char)

    def test_div_id(self):
        divid = tags.AdNode.div_id('A', 'B')
        self.assertEqual(divid, 'adgeletti-ad-div-A-B')

    def test_build_div(self):
        div = tags.AdNode.build_div('FOO')
        self.assertEqual(div, '<div class="adgeletti-ad-div" id="FOO" style="display:none"></div>\n')

    def test_render(self):
        c = template.Context({})
        result = self.node.render(c)
        self.assertIn('<div class="adgeletti-ad-div" id="adgeletti-ad-div-SLOT-A" style="display:none"></div>\n', result)
        self.assertIn('<div class="adgeletti-ad-div" id="adgeletti-ad-div-SLOT-B" style="display:none"></div>\n', result)
        self.assertIn(tags.ADS, c.render_context)
        self.assertIn(tags.BREAKPOINTS, c.render_context)
        self.assertIn(tags.FIRED, c.render_context)
        self.assertSequenceEqual(set(['A', 'B']), c.render_context.get(tags.BREAKPOINTS, []))
        self.assertEqual(c.render_context[tags.ADS]['SLOT']['A'], 'adgeletti-ad-div-SLOT-A')
        self.assertEqual(c.render_context[tags.ADS]['SLOT']['B'], 'adgeletti-ad-div-SLOT-B')

    def test_render_fired(self):
        c = template.Context({})
        c.render_context[tags.FIRED] = True
        result = self.node.render(c)
        self.assertEqual(result, tags.error('{% ad ... %} used after {% adgeletti_go %} used'))


class ParseAdgelettiGoTestCase(TestCase):
    def test_parse_adgeletti_go(self):
        result = tags.parse_adgeletti_go(None, None)
        self.assertIsInstance(result, tags.AdBlock)


class AdBlockTestCase(TestCase):
    def setUp(self):
        self.block = tags.AdBlock()
        self.nodes = [
            tags.AdNode('SLOT1', ['A']),
            tags.AdNode('SLOT2', ['A']),
            tags.AdNode('SLOT2', ['B']),
        ]

        self.site = Site(name='SITE', domain='example.com')
        self.site.save()

    @property
    def context(self):
        context = template.Context({})
        for node in self.nodes:
            node.render(context)
        return context

    def test_render_missing_ads(self):
        result = self.block.render(template.Context({}))
        self.assertEqual(result, tags.error('{% adgeletti_go %} was run without an {% ad ... %}'))

    def test_render_missing_fired(self):
        result = self.block.render(template.Context({tags.ADS: {}}))
        self.assertEqual(result, tags.error('{% adgeletti_go %} was run without an {% ad ... %}'))

    def test_render_fired(self):
        context = self.context
        self.block.render(context) # first call sets FIRED in render context
        result = self.block.render(context)
        self.assertEqual(result, tags.error('{% adgeletti_go %} called more than once'))

    def test_render_no_positions(self):
        result = self.block.render(self.context)
        self.assertEqual(result, tags.error("No ad positions exist for the slots in the page (slots: ['SLOT1', 'SLOT2'])"))

    @mock.patch('adgeletti.templatetags.adgeletti_tags.Site')
    def test_render(self, site):
        site.objects = mock.Mock()
        site.objects.get_current = mock.Mock(return_value=self.site)

        size = Size(width=100, height=100)
        size.save()

        slot1 = AdSlot(label='SLOT1', ad_unit='ADUNIT1', site=self.site)
        slot1.save()

        slot2 = AdSlot(label='SLOT2', ad_unit='ADUNIT2', site=self.site)
        slot2.save()

        pos1a = AdPosition(slot=slot1, breakpoint='A')
        pos1a.save()
        pos1a.sizes.add(size)

        pos2a = AdPosition(slot=slot2, breakpoint='A')
        pos2a.save()
        pos2a.sizes.add(size)

        pos2b = AdPosition(slot=slot2, breakpoint='B')
        pos2b.save()
        pos2b.sizes.add(size)

        result = self.block.render(self.context)
        self.assertIn('<script type="text/javascript">', result)
        self.assertIn('</script>', result)

        sizes = [[size.width, size.height]]
        positions = [
            { 'breakpoint': 'A', 'ad_unit_id': slot1.ad_unit_id(), 'sizes': sizes, 'div_id': tags.AdNode.div_id('SLOT1', 'A'), },
            { 'breakpoint': 'A', 'ad_unit_id': slot2.ad_unit_id(), 'sizes': sizes, 'div_id': tags.AdNode.div_id('SLOT2', 'A'), },
            { 'breakpoint': 'B', 'ad_unit_id': slot2.ad_unit_id(), 'sizes': sizes, 'div_id': tags.AdNode.div_id('SLOT2', 'B'), },
        ]

        for pos in positions:
            self.assertIn('Adgeletti.position(\'%s\');' % json.dumps(pos), result)

