from django.db import models
from django.utils.text import ugettext_lazy as _
from django.contrib.sites.models import Site
from django.conf import settings


class Size(models.Model):
    """The size of an ad.
    """
    width = models.PositiveIntegerField(_(u'width'), help_text=_(u'The width of an ad, in pixels.'))
    height = models.PositiveIntegerField(_(u'height'), help_text=_(u'The height of an ad, in pixels.'))

    class Meta:
        unique_together = ('width', 'height')
        verbose_name = _(u'ad size')

    def __unicode__(self):
        return _(u'%dpx x %dpx') % (self.width, self.height)


class AdPosition(models.Model):
    """An ad unit for display at the selected sizes, for the selected breakpoint
    in the selected slot.
    """
    ad_unit = models.CharField(_(u'Ad unit ID'), max_length=255, unique=True, help_text=_(u'The ad unit ID, without the network ID'))
    slot = models.CharField(_(u'slot'), max_length=255, choices=[(slot, slot) for slot in settings.ADGELETTI_SLOTS])
    breakpoint = models.CharField(_(u'breakpoint'), max_length=255, choices=[(bp, bp) for bp in settings.ADGELETTI_BREAKPOINTS])
    sizes = models.ManyToManyField(Size, verbose_name=_(u'allowed sizes'))
    site = models.ForeignKey(Site, verbose_name=_(u'site'))

    class Meta:
        unique_together = ('ad_unit', 'slot', 'breakpoint', 'site')

    @property
    def ad_unit_id(self):
        return u'%s/%s' % (settings.ADGELETTI_DFP_NETWORK_ID, self.ad_unit)


