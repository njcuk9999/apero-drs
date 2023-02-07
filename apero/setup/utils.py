import sys
from typing import Any

from apero.setup import setup_lang


lang = setup_lang.LangDict()


def catch_sigint(signal_received: Any, frame: Any):
    """
    Deal with Keyboard interupt --> do a sys.exit

    :param signal_received: Any, not used (but expected)
    :param frame: Any, not used (but expected)

    :return: None, exits if this function is called
    """
    # we don't use these we just exit
    _ = signal_received, frame
    # print: Exiting installation script
    print(lang.error('40-001-00075'))
    # raise Keyboard Interrupt
    sys.exit()
