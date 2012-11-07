import re
from django import template
from django.utils.html import escape
from adgeletti.models import AdPosition

ADS = '_adgeletti_ads'
FIRED = '_adgeletti_fired'

register = template.Library()


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
    _clean = re.compile(r'[^-_a-zA-Z0-9]')
    _replace = '-'

    """Emits a div with a unique id for each ad possible at the tag's location.
    """
    def __init__(self, slot, breakpoints):
        self.slot = slot
        self.breakpoints = breakpoints

    @classmethod
    def clean_value(klass, value):
        """Escapes and cleans a value for use as the value of an attribute in
        the ad's div tag.
        """
        return escape(AdNode._clean.sub(AdNode._replace, value))

    @classmethod
    def build_div(klass, slot, breakpoint):
        """Builds an empty div into which an ad is to be placed.
        """
        slot = AdNode.clean_value(slot)
        breakpoint = AdNode.clean_value(breakpoint)
        return '<div class="adgeletti-ad-div" id="%s-%s" adgeletti-slot="%s" adgeletti-breakpoint="%s"></div>' \
                % (slot, breakpoint, slot, breakpoint)

    def render(self, context):
        if FIRED in context and context[FIRED]:
            return error('adgeletti_go has already been fired!')

        if ADS not in context:
            context[ADS] = {}
            context[FIRED] = False

        if self.slot not in context[ADS]:
            context[ADS][self.slot] = []

        context[ADS][self.slot].extend(self.breakpoints)
        return "\n".join((AdNode.build_div(self.slot, bp) for bp in self.breakpoints))


@register.tag(name="adgeletti_go")
def parse_adgeletti_go(parser, token):
    """Parser for adgeletti_go tag. Usage:
        {% adgeletti_go %}
    """
    return AdBlock()


class AdBlock(template.Node):
    """Emits a Javascript lookup table assigned to Adgeletti.ad_data. The table
    stores the following information about ads registered to the page by the ad
    tag:

        Adgeletti[ad_data][BREAKPOINT][SLOT] = { ad_unit_id: '???', sizes: [[?,?], [?,?], ...] }

    ...where sizes is an array of [width, height] pairs (arrays).
    """
    def render(self, context):
        if ADS not in context or FIRED not in context:
            return ''

        if context[FIRED]:
            return error('adgeletti_go has already been fired!')
        else:
            context[FIRED] = True

        # Start building output
        parts = []

        # Get database data
        slots = context[ADS].keys()
        breakpoints = list(set(bp for bp in (context[ADS][slot] for slot in context[ADS])))
        positions = AdPosition.for_site.filter(slot_in=slots, breakpoint_in=breakpoints)

        # Check for obvious errors
        if not slots:
            parts.append(error('No ads have been placed on the page.'))

        if slots and not positions:
            parts.append(error('No AdPositions have been added to the database.'))

        # Always output script and base data structure
        parts.append('<script type="text/javascript">')
        parts.append('var Adgeletti = {ad_data: {}};');

        if positions:
            # Build lookup table
            for pos in positions:
                sizes = '[%s]' % ','.join(['[%d,%d]' % (s.width, s.height) for s in pos.sizes])
                parts.append('Adgeletti.ad_data[%s][%s] = {ad_unit_id: "%s", sizes: [%s]};'
                        % (pos.breakpoint, pos.slot, pos.ad_unit.ad_unit_id, sizes))

        parts.append('</script>')

        return "\n".join(parts)
