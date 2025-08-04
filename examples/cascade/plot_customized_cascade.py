#!/usr/bin/env python3
# Copyright (c) 2023 Intel Corporation
# SPDX-License-Identifier: 0BSD
"""
Customized Cascade
==================

A customized cascade plot.

In this example, we show how to customize a cascade plot by changing the limits
of the y-axis. Although the default limit (of 1) is useful for comparing many
plots side-by-side, in practice it is often useful to be able to zoom-in on
specific regions of data. For example, when dealing with applications that do
not achieve very high levels of architectural efficiency, setting a lower
maximum value for the y-axis can improve readability.

Instead of trying to expose all possible customization options as arguments to
:py:func:`p3analysis.plot.cascade`, the function returns a
:py:class:`p3analysis.plot.CascadePlot` object that provides direct access to library
internals. When using the :py:mod:`matplotlib` backend it is possible to
access the :py:class:`matplotlib.axes.Axes` that were used and subsequently
call any number of :py:mod:`matplotlib` functions. In our example, we can
use :py:meth:`matplotlib.axes.Axes.set_ylim` to update the y-axis.

.. NOTE::
   :py:mod:`matplotlib` is currently the only backend supported by the P3
   Analysis Library, but this is subject to change.

.. TIP::
   If you have any trouble customizing a plot, or the
   :py:class:`~p3analysis.plot.backend.CascadePlot` object does not provide access to
   the internals you are looking for, then please `open an issue
   <https://github.com/P3HPC/p3-analysis-library/issues/new/choose>`_.
"""

# Initialize synthetic performance efficiency data
# (not shown, but available in script download)
# sphinx_gallery_start_ignore
from collections import defaultdict

import pandas as pd

import p3analysis

data = defaultdict(list)
for (i, platform) in enumerate(["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]):
    data["problem"] += ["Synthetic"] * 6
    data["platform"] += [platform] * 6
    data["application"] += [
        "Unportable",
        "Single Target",
        "Multi-Target",
        "Consistent (3%)",
        "Consistent (7%)",
        "Inconsistent",
    ]
    eff = [0] * 6
    eff[0] = 0.1 if i == 0 else 0
    eff[1] = 0.1 if i == 0 else 0.01
    eff[2] = 0.01 if i % 2 else 0.1
    eff[3] = 0.03
    eff[4] = 0.07
    eff[5] = (i + 1) * 0.01
    data["arch eff"] += eff
# sphinx_gallery_end_ignore

# Read performance efficiency data into pandas DataFrame
df = pd.DataFrame(data)

# Generate a cascade plot with custom style options
legend = p3analysis.plot.Legend(loc="center left", bbox_to_anchor=(0.91, 0.225), ncols=2)
pstyle = p3analysis.plot.PlatformStyle(colors="GnBu")
astyle = p3analysis.plot.ApplicationStyle(markers=["x", "s", "p", "h", "H", "v"])
cascade = p3analysis.plot.cascade(df, size=(6, 5), platform_legend=legend, platform_style=pstyle, application_style=astyle)

# Further customize the cascade plot using matplotlib
# In this example, we adjust the range of the y-axis to improve readability
# This may be necessary for studies using architectural efficiency
cascade.get_axes("eff").set_ylim([0, 0.12])
cascade.get_axes("pp").set_ylim([0, 0.12])

cascade.save("customized-cascade.png")
