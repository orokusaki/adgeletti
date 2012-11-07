from django import template
from adgeletti.models import AdPosition

ADS = "_adgeletti_ads"

register = template.Library()

def build_div(slot, breakpoint):
    """Builds an empty div into which an ad is to be placed.
    """
    # TODO escape div id
    return '<div class="adgeletti-ad-div" id="%s-%s" adgeletti-slot="%s" adgeletti-breakpoint="%s"></div>' % (slot, breakpoint, slot, breakpoint)


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
    def __init__(self, slot, breakpoints):
        self.slot = slot
        self.breakpoints = breakpoints

    def render(self, context):
        if ADS not in context:
            context[ADS] = {}

        if self.slot not in context[ADS]:
            context[ADS][self.slot] = []

        context[ADS][self.slot].extend(self.breakpoints)
        return "\n".join((build_div(self.slot, bp) for bp in self.breakpoints))


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
        if ADS not in context:
            return ''

        # Get database data
        positions = AdPosition.for_site.filter(
            slot_in=context[ADS].keys(),
            breakpoint_in=(bp for bp in (context[ADS][slot] for slot in context[ADS])),
        )

        # Start building output
        parts = []
        parts.append('<script type="text/javascript">')
        parts.append('var Adgeletti = {ad_data: {}};');

        # Build lookup table
        for pos in positions:
            sizes = '[%s]' % ','.join(['[%d,%d]' % (s.width, s.height) for s in pos.sizes])
            parts.append('Adgeletti.ad_data[%s][%s] = {ad_unit_id: "%s", sizes: [%s]};'
                    % (pos.breakpoint, pos.slot, pos.ad_unit.ad_unit_id, sizes))

        # Output as Javascript
        parts.append('</script>')
        return "\n".join(parts)
