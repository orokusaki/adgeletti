Adgeletti
=========
The savior of human kind in general, ad ops in particular.

What is it?
=========
Adgeletti is a django module for integration with [DoubleClick for Publishers](http://www.google.com/doubleclick/publishers/solutions/ad-serving.html "DFP").

Goals
=========
1. Simplicity
2. Speed
3. Ease of integration with existing templates
4. Designed for responsive sites

How it works
==========
Adgeletti is configured by defining responsive breakpoints and them mapping them to arbitrary slot names and ad sizes. For example:
  1. Breakpoint FOO is defined as a screen size of 800x600
  2. At breakpoint FOO, slot ABCD is 350x200px

Advertisements are managed and scheduled from within DFP. Ad units are then added to Adgeletti, where they are mapped to a combination defined above. In the template, an ad tag is used to emit HTML and Javascript required to display an ad in a particular ad slot.

For example, to display the ad defined above:

    {% ad "ABCD" FOO %}

If the same ad unit should display in the same location for two different break points:

    {% ad "ABCD" FOO BAR %}

If the same ad unit should display in two different locations for two different break points:

    {% ad "ABCD" FOO %}
    ...
    {% ad "ABCD" BAR %}

Finally, at the bottom of the page, another tag outputs the javascript necessary to toggle these ads:

    {% adgeletti_go %}

Integration
==========
Whatever library you use to trigger breakpoints can then make use of a simple JS API to turn ads on or off.

    var breakpoint = "FOO";
    var slots = ['ABCD', 'DEFG', 'HIJK' ];
    for (var i = 0; i < slots.length; ++i) {
        var slot_name = slots[i];
        adgeletti.display(breakpoint, slot_name);
    }