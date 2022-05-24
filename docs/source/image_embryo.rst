Analyze one embryo
====================

Below are the sequence of steps to segment excitation regions and measure their properties

① convert raw imagestack to temporal derivative
---------------------------------------------------
.. autofunction:: measure.segmentation.bleach_correction
    :noindex:

.. autofunction:: measure.segmentation.group_diff
    :noindex:

② threshold temporal derivative and detect excitation regions
-------------------------------------------------------------------

.. autofunction:: measure.segmentation.excitation
    :noindex:

③ measure summary statistics
-------------------------------

.. autofunction:: measure.recurrence.frequency
    :noindex:

.. autofunction:: measure.recurrence.waittime
    :noindex:

.. autofunction:: measure.contour.findContours
    :noindex:

.. autofunction:: measure.edgespeed.point_velocity
    :noindex:

.. autofunction:: measure.link.connected_components
    :noindex:


④ measure pixel intensity in binary mask at a range of time offsets
--------------------------------------------------------------------------------

.. autofunction:: measure.pixel_intensity.intensity_ts
    :noindex:



