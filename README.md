Adgeletti
=========

The savior of human kind in general, ad ops in particular.

What is it?
-----------

Adgeletti is a django app that facilitates an easy integration with [DoubleClick for Publishers](http://www.google.com/doubleclick/publishers/solutions/ad-serving.html "DFP").

Goals
-----

1.  Simplicity
2.  Efficiency
3.  Ease of integration with existing templates
4.  Designed for responsive sites (works fine with non-responsive sites as well)
5.  Separation of ad scheduling, etc. from ad display

Usage
-----

1.  Define the breakpoints that your website's templates will use, in `settings.py` (e.g., `ADGELETTI_BREAKPOINTS = (u'Mobile', u'Tablet', u'768px', ...)`).
2.  Define an `AdSlot` via the admin, providing a label (slot name), and an ad unit ID.
3.  Create an `AdPosition` for your `AdUnit`, selecting a breakpoint and the sizes of ads allowed.
4.  Use the `{% ad...` template tag to tell Adgeletti where in your page to display the ad.

The following examples will work fine with the steps above, after you load the Adgeletti template tags, like a boss.

    {% load adgeletti_tags %}

To display the ad defined above:

    {% ad AD-01 Mobile %}

If the same ad unit should display in the same location for two different break points:

    {% ad AD-01 Mobile Tablet %}

If the same ad unit should display in two different locations for two different break points:

    {% ad AD-01 Mobile %}
    ...
    {% ad AD-01 Tablet %}

Finally, at the bottom of the page, another tag outputs the javascript necessary to facilitate displaying the ads:

    {% adgeletti_go %}

Integration
-----------

Integration is simple. Call the `Adgeletti.display` function, providing the breakpoint you'd like to display ads for.

    // The following would cause any ads in the page with a "Mobile" breakpoint
    // to be displayed. This should be done within a document ready handler, or
    // some time after the document ready event has occurred, to ensure the
    // lucky charms are in order before an ad is displayed.
    Adgeletti.display('Mobile');

Dependencies
------------

1.  Django 1.3
2.  `contrib.sites`
3.  The Google GPT script (e.g. //www.googletagservices.com/tag/js/gpt.js)
