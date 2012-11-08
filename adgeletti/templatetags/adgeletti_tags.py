import re
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
    return '<!-- %s -->' % escape(text)


@register.tag(name="ad")
def parse_ad(parser, token):
    """Parser for ad tag. Usage:
        {% ad SLOT BREAKPOINT [BREAKPOINT ...] %}
    """
    args = token.split_contents()

    if len(args) < 2:
        raise template.TemplateSyntaxError("usage: {% ad SLOT BREAKPOINT [BREAKPOINT ...] %}")

    slot = args[0]
    breakpoints = args[1:]
    return AdNode(slot, breakpoints)


class AdNode(template.Node):
    """Emits a div with a unique id for each ad possible at the tag's location.
    """
    _clean = re.compile(r'[^-_a-zA-Z0-9]')
    _replace = '-'

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
        return "%s-%s" % (slot, breakpoint)

    @staticmethod
    def build_div(div_id, slot, breakpoint):
        """Builds an empty div into which an ad is to be placed.
        """
        div_id = AdNode.clean_value(div_id)
        slot = AdNode.clean_value(slot)
        breakpoint = AdNode.clean_value(breakpoint)
        return '<div class="adgeletti-ad-div" id="%s" adgeletti-slot="%s" adgeletti-breakpoint="%s"></div>' \
            % (div_id, slot, breakpoint)

    def render(self, context):
        if FIRED in context and context[FIRED]:
            return error('adgeletti_go has already been fired.')

        if ADS not in context:
            context[ADS] = {}
            context[FIRED] = False
            context[BREAKPOINTS] = set([])

        if self.slot not in context[ADS]:
            context[ADS][self.slot] = {}

        buf = cStringIO.StringIO()

        for breakpoint in self.breakpoints:
            div_id = AdNode.div_id(self.slot, breakpoint)
            div = AdNode.build_div(div_id, self.slot, breakpoint)

            # Add breakpoint to global set
            context[BREAKPOINTS].add(breakpoint)

            # Add to context and output
            if breakpoint not in context[ADS][self.slot]:
                context[ADS][self.slot][breakpoint] = div_id
                buf.write(div)
                buf.write('\n')

        content = buf.getvalue()
        buf.close()
        return content


@register.tag(name="adgeletti_go")
def parse_adgeletti_go(parser, token):
    """Parser for adgeletti_go tag. Usage:
        {% adgeletti_go %}
    """
    return AdBlock()


class AdBlock(template.Node):
    """Emits a <script type="text/javascript"> tag with code similar to the
    following example, as a means to define an ad position.

        Adgeletti.position("Mobile", "AD-UNIT-ID-1", "DIV-ID-1", [[320,50]]);

    ...where sizes is an array of [width, height] pairs (arrays).
    """
    # Template for ad definition
    POSITION_TPL = u'Adgeletti.position("{b}", "{a}", {s}, "{d}");'

    def render(self, context):
        if ADS not in context or FIRED not in context:
            return u''

        if context[FIRED]:
            return error(u'adgeletti_go has already been fired.')
        else:
            context[FIRED] = True

        # Start building output
        buf = cStringIO.StringIO()

        # Get database data
        slots = context[ADS].keys()
        breakpoints = context[BREAKPOINTS]
        positions = AdPosition.objects.filter(
            ad_unit__site=Site.objects.get_current(),
            slot__in=slots,
            breakpoint__in=breakpoints,
        )

        # Check for obvious errors
        if not slots:
            buf.write(error(u'No ads have been placed on the page.\n'))

        if slots and not positions:
            buf.write(error(u'No AdPositions have been added to the database.\n'))

        # Always output script and base data structure
        buf.write(u'<script type="text/javascript">\n')

        # Output nothing if no positions found at all
        if positions:
            for pos in positions:
                div_id = context[ADS][pos.slot][pos.breakpoint]
                sizes = '[' + ','.join(['[%d,%d]' % (s.width, s.height) for s in pos.sizes]) + ']'

                buf.write(
                    AdBlock.POSITION_TPL.format(
                        b=pos.breakpoint,
                        a=pos.ad_unit.ad_unit_id,
                        s=sizes,
                        d=div_id,
                    )
                )
                buf.write('\n')

        buf.write(u'</script>\n')
        content = buf.getvalue()
        buf.close()
        return content

