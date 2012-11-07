Adgeletti
=========

The savior of human kind in general, ad ops in particular.

What is it?
==========

Adgeletti is a django app that facilitates an easy integration with [DoubleClick for Publishers](http://www.google.com/doubleclick/publishers/solutions/ad-serving.html "DFP").

Goals
=========

1.  Simplicity (just a few quick additions to your `settings.py` module, including adding `adgeletti` to your `INSTALLED_APPS`)
2.  Efficiency (minimal queries)
3.  Ease of integration with existing templates (2 template tags, nothing else)
4.  Designed for responsive sites (define breakpoints for ad display)
5.  Separation of ad scheduling and management from display (ads are managed in Google's DFP interface)

How it works
============

Adgeletti is configured by defining responsive breakpoints and them mapping them to arbitrary slot names and ad sizes.

Usage
-----

1.  Define ad slots in `settings.py` (e.g., `ADGELETTI_SLOTS = (u'AD-01', u'AD-02',)`)
2.  Define breakpoints in `settings.py` (e.g., `ADGELETTI_BREAKPOINTS = (u'Mobile', u'Tablet', u'Wired',)`)
3.  Use the `{% ad...` tag to tell Adgeletti where in your page to display the ads (example below)
4.  Create an `AdUnit` objects via the admin.
5.  Create an `AdPosition` for the `AdUnit`.

The following examples will work fine with the steps above, after you load the Adgeletti temlpate tags.

    {% load adgeletti_tags %}

To display the ad defined above:

    {% ad AD-01 Mobile %}

If the same ad unit should display in the same location for two different break points:

    {% ad AD-01 Mobile, Tablet %}

If the same ad unit should display in two different locations for two different break points:

    {% ad AD-01 Mobile %}
    ...
    {% ad AD-01 Tablet %}

Finally, at the bottom of the page, another tag outputs the javascript necessary to facilitate displaying the ads:

    {% adgeletti_init %}

Integration
===========

Integration is simple. Trigger a jquery event called "adgeletti_display", providing the breakpoint you'd like to display for.

Example
-------

    // The following would cause any ads in the page with a "Mobile" breakpoint
    // to be shown, if the element with the `id="show_mobile_ads"` was clicked
    $('#show_mobile_ads').click(function(e){
        $('body').trigger('adgeletti_display', 'Mobile');
    });
