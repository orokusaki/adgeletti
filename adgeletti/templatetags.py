from django import template

register = template.Library()

@register.tag(name="ad")
def parse_ad(parser, token):
    args = token.split_contents()

    if len(args) < 2:
        raise template.TemplateSyntaxError("usage: {% ad SLOT BREAKPOINT [BREAKPOINT ...] %}")

    slot = args[0]
    breakpoints = args[1:]
    return AdNode(slot, breakpoints)


class AdNode(template.Node):
    def __init__(self, slot, breakpoints):
        self.slot = slot
        self.breakpoints = breakpoints

    def render(self, context):
        if 'adgeletti_ads' not in context:
            context['adgeletti_ads'] = []
