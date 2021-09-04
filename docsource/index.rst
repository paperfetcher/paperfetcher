.. paperfetcher documentation master file, created by
   sphinx-quickstart on Sat Sep  4 16:24:49 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

###############################
paperfetcher
###############################

:Release: |release|

Paperfetcher is a Python package to mine papers for systematic reviews. Paperfetcher
works with Python 3, and has been tested for Python 3.7+.

You can either install paperfetcher using `pip`_, or alternatively, clone the source code from
Github and install it from source.

.. _`pip`: https://pip.pypa.io/en/stable/

Installation with pip
*********************

1. `Install pip`_

.. _`Install pip`: https://pip.pypa.io/en/stable/getting-started/

2. Install paperfetcher using pip

Open a terminal window and run

.. code-block:: bash

  pip install paperfetcher

**OR**

Installation from source (requires git)
***************************************

**Source code** is available from
`https://github.com/paperfetcher/paperfetcher`_

1. Obtain the sources with `git`_

.. code-block:: bash

  git clone https://github.com/paperfetcher/paperfetcher.git

.. _`https://github.com/paperfetcher/paperfetcher`: https://github.com/paperfetcher/paperfetcher
.. _git: https://git-scm.com/

2. Install package

Open a terminal window in the paperfetcher directory and run

.. code-block:: bash

  python setup.py install


Running tests (optional)
**************************

To run unit tests:

.. code-block:: bash

  cd tests/tests_unit
  pytest

To run integration tests:

.. code-block:: bash

  cd tests/tests_integration
  pytest

Usage
**************************

See the example Jupyter notebooks below to get started:

1. `Crossref hand-search getting started guide`_
2. Crossref snowball-search getting started guide (coming soon!)

.. _`Crossref hand-search getting started guide`: https://nbviewer.jupyter.org/github/paperfetcher/paperfetcher/blob/master/examples/Crossref_hand_search.ipynb

Once you understand the workflow, read the Module Documentation below to
learn more about how to use paperfetcher's various modules, classes and functions.

========================================

.. toctree::
   :maxdepth: 2
   :caption: Module documentation:

   paperfetcher

========================================

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
