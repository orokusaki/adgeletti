import mock
from django import template
from django.utils.unittest import TestCase
from adgeletti.templatetags import adgeletti_tags as tags

class TemplateTestCase(TestCase):
    def render(self, template_string, **kwargs):
        t = template.Template(template_string)
        c = template.Context(kwargs)
        return t.render(c)


class ErrorTestCase(TestCase):
    @mock.patch('adgeletti.templatetags.adgeletti_tags.escape')
    def test_error_strings(self, escape):
        escape.return_value = 'BAR'
        error = tags.error('FOO')
        escape.assert_called_with('FOO')
        self.assertEqual(error, '<!-- BAR -->\n')


class ParseAdTestCase(TemplateTestCase):
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
        self.assertEqual(exc.exception.message, u'usage: {% ad SLOT BREAKPOINT [BREAKPOINT ...] %}')

