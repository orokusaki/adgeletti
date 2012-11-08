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


class AdSlot(models.Model):
    """An individual slot configuration for a site.
    """
    label = models.CharField(_(u'Label'), max_length=25, help_text=_(u'Identifier for slot to be used on the page.'))
    site = models.ForeignKey(Site, verbose_name=_(u'site'))
    ad_unit = models.CharField(_(u'Ad unit ID'), max_length=255, help_text=_(u'The ad unit ID, without the network ID.'))

    class Meta:
        unique_together = ('label', 'site')

    def __unicode__(self):
        return _(u'%s (%s)' % (self.label, self.site))

    @property
    def ad_unit_id(self):
        return u'%s/%s' % (settings.ADGELETTI_DFP_NETWORK_ID, self.ad_unit)


class AdPosition(models.Model):
    """Configures how a slot is to be displayed for a given breakpoint.
    """
    slot = models.ForeignKey(AdSlot)
    breakpoint = models.CharField(_(u'breakpoint'), max_length=25, choices=[(bp, bp) for bp in settings.ADGELETTI_BREAKPOINTS])
    sizes = models.ManyToManyField(Size, verbose_name=_(u'allowed sizes'))

    class Meta:
        unique_together = ('slot', 'breakpoint')

