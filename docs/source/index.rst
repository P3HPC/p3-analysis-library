Performance, Portability, and Productivity Analysis Library
===========================================================

.. toctree::
   :maxdepth: 1
   :hidden:
   :caption: Introduction

   Getting Started <self>
   analysis
   data

.. toctree::
   :maxdepth: 1
   :hidden:
   :caption: Tutorial

   examples/index
   case-studies/index

.. toctree::
   :maxdepth: 1
   :hidden:
   :caption: Reference

   p3analysis

.. toctree::
   :maxdepth: 1
   :hidden:
   :caption: Contributing

   How to Contribute <https://github.com/P3HPC/p3-analysis-library/blob/main/CONTRIBUTING.md>
   GitHub <https://github.com/P3HPC/p3-analysis-library>
   notices-and-disclaimers

The Performance, Portability, and Productivity Analysis Library (P3 Analysis
Library) enables a simpler workflow for the collection and interpretation of P3
data.

- Compute :doc:`metrics <p3analysis.metrics>` like "performance portability" and
  "code divergence" to quantify the trade-offs between performance, portability
  and productivity made by applications targeting multiple platforms.

- :doc:`Plot <p3analysis.plot>` cascades and navigation charts to visualize and gain
  deeper insight into the "performance portability" and "code divergence"
  scores achieved by different applications.


Installation
############

.. warning::
   As we prepare the P3 Analysis Library for its 1.0 release, we have updated
   the online documentation to reflect the latest development version.
   This documentation should be considered *unstable*.

The latest release of the P3 Analysis Library is version 0.1.0-alpha. To
download and install this release, run the following::

    $ git clone --branch v0.1.0-alpha https://github.com/P3HPC/p3-analysis-library.git
    $ cd p3-analysis-library
    $ pip install .

We strongly recommend installing the P3 Analysis Library within a `virtual
environment`_.

.. _`virtual environment`: https://docs.python.org/3/library/venv.html


Getting Started
###############

As a library, the P3 Analysis Library does not provide user-facing scripts for
preset analyses. Rather, the library provides routines for manipulating and
visualizing data in support of common P3 analysis tasks.

Using the P3 Analysis Library effectively requires:

1. **A basic understanding of P3 analysis and related terminology.**

   A brief refresher can be found `here <analysis.html>`__, and a high-level
   overview can be found in papers like
   "`Navigating Performance, Portability and Productivity`_".

   .. _here: analysis.html
   .. _Navigating Performance, Portability and Productivity: https://doi.org/10.1109/MCSE.2021.3097276

2. **P3 data stored in one of the expected formats.**

   The library does not interact with the filesystem, and expects data to be
   prepared and stored in `Pandas`_ DataFrames with specific column names.

   A guide for collecting and structuring P3 data can be found `here <data.html>`__.

   .. _Pandas: https://pandas.pydata.org/

Simple examples of using the library are available on the `examples`_ page.
Complete end-to-end examples, using real data, are available on the `case
studies`_ page.

.. _examples: examples/index.html
.. _case studies: case-studies/index.html
