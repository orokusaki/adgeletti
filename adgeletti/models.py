from django.db import models
from django.contrib.sites.models import Site
from django.contrib.sites.managers import CurrentSiteManager
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
    ad_unit_id = models.CharField(max_length=255, unique=True)
    sizes = models.ManyToManyField(Size)
    site = models.ForeignKeyField(Site)

    objects = CurrentSiteManager()


class Ad(models.Model):
    """Selects the AdUnit to display in a Slot at a particular Breakpoint.
    """
    slot = models.CharField(max_length=50, choices=settings.ADGELETTI_SLOTS)
    breakpoint = models.CharField(max_length=50, choices=settings.ADGETLETTI_BREAKPOINTS)
    ad_unit = models.ForeignKey(AdUnit)

    class Meta:
        unique_together = ('slot', 'breakpoint', 'ad_unit')
