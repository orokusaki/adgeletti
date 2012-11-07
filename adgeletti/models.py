from django.db import models
from django.contrib.sites.models import Site
from django.conf import settings

class Size(models.Model):
    """Defines an ad size to make available for a Breakpoint.
    """
    width = models.PositiveIntegerField()
    height = models.PositiveIntegerField()

    class Meta:
        unique_together = ('width', 'height')

    def __unicode__(self):
        return '%dpx x %dpx' % (self.width, self.height)


class AdUnit(models.Model):
    """Represents an ad unit and a configured size that it can support.
    """
    unit_id = models.CharField(max_length=255, unique=True)
    site = models.ForeignKey(Site)

    def ad_unit_id(self):
        return '%s/%s' % (settings.ADGELETTI_NETWORK_ID, self.unit_id)


class AdPosition(models.Model):
    """Selects the AdUnit to display in a Slot at a particular Breakpoint.
    """
    slot = models.CharField(max_length=50, choices=settings.ADGELETTI_SLOTS)
    breakpoint = models.CharField(max_length=50, choices=settings.ADGELETTI_BREAKPOINTS)
    sizes = models.ManyToManyField(Size)
    ad_unit = models.ForeignKey(AdUnit)

    class Meta:
        unique_together = ('slot', 'breakpoint', 'ad_unit')
