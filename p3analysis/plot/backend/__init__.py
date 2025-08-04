# Copyright (c) 2022-2023 Intel Corporation
# SPDX-License-Identifier: MIT
"""
Contains backend-specific interfaces for customizing plots.

.. TIP::
   If you have any trouble customizing a plot, or the objects in this module
   do not provide access to the internals you are looking for, then please
   `open an issue
   <https://github.com/P3HPC/p3-analysis-library/issues/new/choose>`_.
"""

import itertools
import string

__all__ = [
    "Plot",
    "CascadePlot",
    "NavChart",
]


class Plot:
    """
    Base class for plot objects.
    """

    def __init__(self, backend):
        self.backend = backend

    def get_backend(self):
        """
        Returns
        -------
        str
            The name of the backend used to generate the plot.
        """
        return self.backend


class CascadePlot(Plot):
    """
    Base class for cascade plot objects.
    """

    def __init__(self, backend):
        super().__init__(backend)


class NavChart(Plot):
    """
    Base class for navigation chart objects.
    """

    def __init__(self, backend):
        super().__init__(backend)


def _get_platform_labels(platforms: list[str]) -> dict[str, str]:
    """
    Parameters
    ----------
    platforms : list[str]
        A list of platform names to associate with labels.

    Returns
    -------
    dict[str, str]:
        A mapping from platform names to unique labels.
    """
    if len(platforms) <= len(string.ascii_uppercase):
        labels = string.ascii_uppercase
    elif len(platforms) <= len(string.ascii_uppercase) ** 2:
        labels = []
        for x, y in itertools.product(string.ascii_uppercase, repeat=2):
            labels.append(f"{x}{y}")
    else:
        raise RuntimeError(
            "The number of platforms supported by cascade plots is "
            + f"currently limited to {len(string.ascii_uppercase)**2}.",
        )
    return dict(zip(platforms, labels))
