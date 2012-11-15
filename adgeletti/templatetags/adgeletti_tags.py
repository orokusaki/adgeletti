import re
import json
import cStringIO

from django import template
from django.contrib.sites.models import Site
from django.utils.html import escape

from adgeletti.models import AdPosition


register = template.Library()

ADS = '_adgeletti_ads'
FIRED = '_adgeletti_fired'
BREAKPOINTS = '_adgeletti_breakpoints'


def error(text):
    """Formats error text as an (escaped) HTML comment.
    """
    return '<!-- %s -->\n' % escape(text)


@register.tag(name='ad')
def parse_ad(parser, token):
    """Parser for ad tag. Usage:
        {% ad SLOT BREAKPOINT [BREAKPOINT ...] %}
    """
    args = token.split_contents()

    if len(args) < 3:
        raise template.TemplateSyntaxError(u'usage: {% ad SLOT BREAKPOINT [BREAKPOINT ...] %}')

    slot = args[1]
    breakpoints = args[2:]
    return AdNode(slot, breakpoints)


class AdNode(template.Node):
    """Emits a div with a unique id for each ad possible at the tag's location.
    """
    _clean = re.compile(r'[^-_a-zA-Z0-9]')
    _replace = u'-'

    def __init__(self, slot, breakpoints):
        self.slot = slot
        self.breakpoints = breakpoints

    @staticmethod
    def clean_value(value):
        """Escapes and cleans a value for use as the value of an attribute in
        the ad's div tag.
        """
        return escape(AdNode._clean.sub(AdNode._replace, value))

    @staticmethod
    def div_id(slot, breakpoint):
        """Returns a string (unescaped) that may be used as the id attribute for
        an ad's div.
        """
        return u'adgeletti-ad-div-%s-%s' % (slot, breakpoint)

    @staticmethod
    def build_div(div_id):
        """Builds an empty div into which an ad is to be placed.
        """
        div_id = AdNode.clean_value(div_id)
        return '<div class="adgeletti-ad-div" id="%s" style="display:none"></div>\n' % div_id

    def render(self, context):
        if context.render_context.get(FIRED, False):
            return error(u'{% ad ... %} used after {% adgeletti_go %} used')

        if ADS not in context.render_context:
            context.render_context[ADS] = {}
            context.render_context[FIRED] = False
            context.render_context[BREAKPOINTS] = set([])

        if self.slot not in context.render_context[ADS]:
            context.render_context[ADS][self.slot] = {}

        buf = cStringIO.StringIO()

        for breakpoint in self.breakpoints:
            div_id = AdNode.div_id(self.slot, breakpoint)
            div = AdNode.build_div(div_id)

            # Add breakpoint to global set
            context.render_context[BREAKPOINTS].add(breakpoint)

            # Add to context and output
            if breakpoint not in context.render_context[ADS][self.slot]:
                context.render_context[ADS][self.slot][breakpoint] = div_id
                buf.write(div)

        content = buf.getvalue()
        buf.close()

        return content


@register.tag(name='adgeletti_go')
def parse_adgeletti_go(parser, token):
    """Parser for adgeletti_go tag. Usage:
        {% adgeletti_go %}
    """
    return AdBlock()


class AdBlock(template.Node):
    """Emits a <script type="text/javascript"> tag with code similar to the
    following example, as a means to define an ad position.

        Adgeletti.position('{"breakpoint": "Mobile", "ad_unit_id": "AD-UNIT-ID-1", "div_id": "DIV-ID-1", "sizes": [[320,50]]}');

    ...where sizes is an array of [width, height] pairs (arrays).
    """
    # Template for ad definition
    POSITION_TPL = u'Adgeletti.position(\'%s\');'

    def render(self, context):
        if ADS not in context.render_context or FIRED not in context.render_context:
            return error(u'{% adgeletti_go %} was run without an {% ad ... %}')

        if context.render_context[FIRED]:
            return error(u'{% adgeletti_go %} already used, but used again')
        else:
            context.render_context[FIRED] = True

        # Start building output
        buf = cStringIO.StringIO()

        # Get database data
        slots = context.render_context[ADS].keys()
        breakpoints = context.render_context[BREAKPOINTS]
        positions = AdPosition.objects.filter(
            slot__site=Site.objects.get_current(),
            slot__label__in=slots,
            breakpoint__in=breakpoints,
        )

        if slots and not positions:
            buf.write(error(u'No ad positions exist for the slots in the page - slots were %s' % slots))

        # Always output script and base data structure
        buf.write(u'<script type="text/javascript">\n')

        # Loop through each ``AdPosition`` and emit an `Adgeletti.position`
        # call for each, providing the data as JSON
        for pos in positions:
            _position_data = {
                'breakpoint': pos.breakpoint,
                'ad_unit_id': pos.slot.ad_unit_id,
                'sizes': [
                    [size.width, size.height] for size in pos.sizes.all()
                ],
                'div_id': context.render_context[ADS][slot][breakpoint],
            }
            buf.write(AdBlock.POSITION_TPL % (json.dumps(_position_data),))

            buf.write(u'\n')

        buf.write(u'</script>\n')
        content = buf.getvalue()
        buf.close()

        return content
