import re

from django import template
from django.utils.html import escape
from django.contrib.sites.models import Site

from adgeletti.models import AdPosition


register = template.Library()

ADS = '_adgeletti_ads'
FIRED = '_adgeletti_fired'


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

    @staticmethod
    def clean_value(value):
        """Escapes and cleans a value for use as the value of an attribute in
        the ad's div tag.
        """
        return escape(AdNode._clean.sub(AdNode._replace, value))

    @staticmethod
    def build_div(slot, breakpoint):
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
    """
    Emits a <script type="text/javascript"> tag with code similar to the
    following example, as a means to define an ad position.

        Adgeletti.position("Mobile", "AD-UNIT-ID-1", "DIV-ID-1", [[320,50]]);

    ...where sizes is an array of [width, height] pairs (arrays).
    """
    def render(self, context):
        if ADS not in context or FIRED not in context:
            return u''

        if context[FIRED]:
            return error(u'adgeletti_go has already been fired!')
        else:
            context[FIRED] = True

        # Start building output
        parts = []

        # Get database data
        slots = context[ADS].keys()
        breakpoints = list(
            set(bp for bp in (context[ADS][slot] for slot in context[ADS])))
        positions = AdPosition.objects.filter(
            ad_unit__site=Site.objects.get_current(), slot__in=slots,
            breakpoint__in=breakpoints)

        # Check for obvious errors
        if not slots:
            parts.append(
                error(u'No ads have been placed on the page.'))

        if slots and not positions:
            parts.append(
                error(u'No AdPositions have been added to the database.'))

        # Always output script and base data structure
        parts.append(u'<script type="text/javascript">')

        # Template for ad definition
        POSITION_TPL = u'Adgeletti.position("{b}", "{a}", {s}, "{d}");'

        if positions:
            # Build lookup table
            for pos in positions:
                sizes = u'[%s]' % ','.join(
                    ['[%d,%d]' % (s.width, s.height) for s in pos.sizes])
                parts.append(
                    POSITION_TPL.format(
                        b=pos.breakpoint, a=pos.ad_unit.ad_unit_id, s=sizes,
                        d=pos.div_id))


                        # TODO: Address this tomorrow when I have to chance to
                        # chat with Jeff about ``pos.div_id`` being added, and
                        # pos being a dict that is generated higher up than in
                        # this method, and passed into the context for grabbing
                        # here - ``POSS[BREAKPOINT] = [slot, ...]`` needs to be
                        # the case as well for this to happen... too tired, too
                        # noisy at SBUX, gotta head out :( (also double check
                        # that `size` for `pubads().display(...)` can indeed
                        # be a list of sizes, vs a single size... why the hell
                        # do they document its syntax in a way that implies
                        # `size` is a single value?)


        parts.append(u'</script>')

        return u'\n'.join(parts)
