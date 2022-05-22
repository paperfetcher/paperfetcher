.. paperfetcher documentation master file, created by
   sphinx-quickstart on Sat Sep  4 16:24:49 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

###############################
paperfetcher
###############################

:Release: |release|

Paperfetcher is a Python package to automate handsearching and citation searching
(snowballing) for systematic reviews. To learn more about Paperfetcher, visit
`paperfetcher.github.io`_.

.. _`paperfetcher.github.io`: https://paperfetcher.github.io/

Paperfetcher works with Python 3.7+.

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


Running tests (if installed from source)
**************************

You can run tests to make sure that paperfetcher is working correctly on your system.

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

To get started, browse the Jupyter notebooks in the examples/ directory in this
repository.

Once you understand the workflow, read the Module Documentation below to
learn more about paperfetcher's various modules, classes and functions.


The Team
******************

Paperfetcher was developed by `Akash Pallath`_ at the `University of Pennsylvania`_ and `Qiyang Zhang`_ at the `Johns Hopkins University`_.

.. _`Akash Pallath`: https://apallath.github.io
.. _`University of Pennsylvania`: https://www.upenn.edu
.. _`Qiyang Zhang`: https://qiyangzh.github.io
.. _`Johns Hopkins University`: https://www.jhu.edu

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
