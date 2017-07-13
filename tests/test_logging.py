import pysanity


def test_get_logger():
    import logging
    sane_logging = pysanity.make_proxy(logging)

    assert logging == sane_logging
    assert sane_logging.get_logger is logging.getLogger
    assert sane_logging.get_logger(__name__) is logging.getLogger(__name__)
