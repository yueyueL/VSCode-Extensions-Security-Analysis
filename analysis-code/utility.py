
"""
    Utility file, stores shared information.
"""

import logging
import signal


TEST = False

if TEST:  # To test, e.g., the examples
    PRINT_DEBUG = True  # Debug prints
else:
    PRINT_DEBUG = False  # No debug prints, sometimes still logging


def print_separator():
    if PRINT_DEBUG:
        print('------------------------')


def print_info(my_info):
    """ For testing, easier to get info printed, otherwise logged. """

    if PRINT_DEBUG:
        print(my_info)
    else:
        logging.info(my_info)


class Timeout:
    """ Timeout class using ALARM signal. Debug for provenance. """

    class Timeout(Exception):
        """ Timeout class throwing an exception. """

    def __init__(self, sec):
        self.sec = sec

    def __enter__(self):
        signal.signal(signal.SIGALRM, self.raise_timeout)
        signal.alarm(self.sec)

    def __exit__(self, *args):
        signal.alarm(0)  # disable alarm

    def raise_timeout(self, *args):
        raise Timeout.Timeout()
