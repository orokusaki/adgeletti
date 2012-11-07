from django.db import models
from django.contrib.sites.models import Site
from django.contrib.sites.managers import CurrentSiteManager

class Slot(models.Model):
    """Defines an advertising slot that may be placed in a template.
    """
    label = models.CharField(max_length=25, unique=True)

    def __unicode__(self):
        return self.label


class Breakpoint(models.Model):
    """Defines a responsive breakpoint for which a Slot may be displayed.
    """
    label = models.CharField(max_length=25, unique=True)

    def __unicode__(self):
        return self.label


class Size:
    """Defines an ad size to make available for a Breakpoint.
    """
    width = models.PositiveIntegerField()
    height = models.PositiveIntegerField()

    class Meta:
        unique_together = ('width', 'height')

    def __unicode__(self):
        return '%dpx x %dpx' % (self.width, self.height)


class AdUnit:
    size = models.ForeignKey(Size)
    ad_unit_id = models.CharField(max_length=255)

    class Meta:
        unique_together = ('size', 'ad_unit_id')


class Ad(models.Model):
    """Selects the size of ad that displays in a Slot at a particular
    Breakpoint.
    """
    sites = models.ManyToManyField(Site)
    slot = models.ForeignKey(Slot)
    breakpoint = models.ForeignKey(Breakpoint)
    ad_unit = models.ForeignKey(AdUnit)

    objects = CurrentSiteManager()
    all_sites = models.Manager()

    def __unicode__(self):
        return 'Ad <%s/%s/%s>' % (self.slot, self.breakpoint, self.size)
