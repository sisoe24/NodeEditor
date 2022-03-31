# coding: utf-8
from __future__ import print_function

import os
from random import randint

from PySide2.QtGui import QPalette, QColor


def widget_color(func):
    """Internal Test function for coloring layouts."""

    def inner_wrapper(*args, **kwargs):

        self = args[0]
        func(self)

        # ui_state_file = '.color_state'
        # if not os.path.exists(ui_state_file):
        #     return

        # with open(ui_state_file) as state_file:
        #     state = state_file.read().strip()

        #     if state == 'False':
        #         return

        self.setAutoFillBackground(True)
        palette = QPalette()

        color = ''
        if color:
            palette.setColor(QPalette.Window, QColor(color))
        else:
            palette.setColor(QPalette.Window, QColor(
                randint(0, 256), randint(0, 256), randint(0, 256)))

        self.setPalette(palette)
    return inner_wrapper
