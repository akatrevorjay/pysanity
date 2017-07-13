pysanity
========

Emulates sanity for other people's dirty ass non-pep compliant code via only the /dirtiest/ of means.

Tested with Python 2.7, 3.5.

|Test Status| |Coverage Status| |Documentation Status|

-  PyPi: https://pypi.python.org/pypi/pysanity

And that means?
---------------

Hi! I'm `pysanity` and I turn:

.. code:: python

    import logging
    log = logging.getLogger(__name__)

Into the much less brain numbing:

.. code:: python

    from pysanity import logging
    log = logging.get_logger(__name__)

All the while keeping your precious code completion working as expected thanks to a not grossly over-dynamic nature.

You're welcome for my existence on PyPi.

Logging you say?
----------------

*Hint:* Try this out and stop accepting needless boilerplate in your code, stdlib or not:

.. code:: python

    import logging
    import logging.config
    import inspect


    def _namespace_from_calling_context():
        """
        Derive a namespace from the module containing the caller's caller.

        :return str: the fully qualified python name of a module.
        """
        return inspect.currentframe().f_back.f_back.f_globals['__name__']


    def get_logger(name=None):
        """
        Gets a logger instance with sensible defaults according to caller context.

        :param str name: Logger name. Defaults to caller's `__name__`.
        :return logging.Logger: Logger instance
        """
        if not name:
            name = _namespace_from_calling_context()

        return logging.getLogger(name)


Installation
------------

.. code:: sh

    pip install pysanity


Running tests
-------------

Tox is used to handle testing multiple python versions.

.. code:: sh

    tox


.. |Test Status| image:: https://circleci.com/gh/akatrevorjay/pysanity.svg?style=svg
   :target: https://circleci.com/gh/akatrevorjay/pysanity
.. |Coverage Status| image:: https://coveralls.io/repos/akatrevorjay/pysanity/badge.svg?branch=develop&service=github
   :target: https://coveralls.io/github/akatrevorjay/pysanity?branch=develop
.. |Documentation Status| image:: https://readthedocs.org/projects/pysanity/badge/?version=latest
   :target: http://pysanity.readthedocs.org/en/latest/?badge=latest

