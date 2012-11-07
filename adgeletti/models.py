from django.db import models
from django.contrib.sites.models import Site
from django.conf import settings

class Size(models.Model):
    """Defines an ad size to make available for a Breakpoint.
    """
    width = models.PositiveIntegerField(help_text="The width of the ad in pixels.")
    height = models.PositiveIntegerField(help_text="The height of the ad in pixels.")

    class Meta:
        unique_together = ('width', 'height')

    def __unicode__(self):
        return '%dpx x %dpx' % (self.width, self.height)


class AdUnit(models.Model):
    """Represents an ad unit and a configured size that it can support.
    """
    ad_unit = models.CharField(max_length=255, unique=True, help_text="The ad unit id, without the network ID")
    site = models.ForeignKey(Site)

    @property
    def ad_unit_id(self):
        return '%s/%s' % (settings.ADGELETTI_DFP_NETWORK_ID, self.ad_unit)


class AdPosition(models.Model):
    """Selects the AdUnit to display in a Slot at a particular Breakpoint.
    """
    slot = models.CharField(max_length=50, choices=settings.ADGELETTI_SLOTS)
    breakpoint = models.CharField(max_length=50, choices=settings.ADGELETTI_BREAKPOINTS)
    sizes = models.ManyToManyField(Size)
    ad_unit = models.ForeignKey(AdUnit)

    class Meta:
        unique_together = ('slot', 'breakpoint', 'ad_unit')
