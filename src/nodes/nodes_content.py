
import logging

from PySide2.QtCore import Qt
from PySide2.QtWidgets import (
    QFormLayout,
    QSpacerItem,
    QLabel,
    QVBoxLayout,
    QWidget
)

LOGGER = logging.getLogger('nodeeditor.master_node')


class NodeContent(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.inputs = []
        self.outputs = []

        self._layout = QVBoxLayout()
        self._layout.setContentsMargins(10, 10, 10, 10)
        self._layout.addSpacerItem(QSpacerItem(0, 0))
        self._layout.setSpacing(15)
        self.setLayout(self._layout)

    def _is_widget(func):
        def wrapper(*args):
            widget = args[1]
            if isinstance(widget, QWidget):
                return func(*args)
            LOGGER.error('Item is not a child of QObject: %s %s',
                         type(widget), widget)
        return wrapper

    @_is_widget
    def add_widget(self, widget, index=0):
        """Add a widget into the node graphics

        A widget is not going to have any input or output sockets connected.

        Args:
            widget (any): A instance of a QWidget class.
        """
        self._layout.insertWidget(index, widget)

    @_is_widget
    def add_input(self, widget, index=0):
        """Add an input widget with a socket.

        Args:
            widget (any): A instance of a QWidget class.
        """
        self.inputs.append(widget)
        self._layout.insertWidget(index, widget)

    def add_input_widget(self, label: str, widget, index=0):
        """Add an input widget with a socket.

        Args:
            widget (any): A instance of a QWidget class.
        """
        self.inputs.append(widget)
        _form = QFormLayout()
        _form.addRow(QLabel(label), widget)
        self._layout.insertLayout(index, _form)

    def add_output(self, text: str, index=0, value=""):
        """Add an output widget with a socket.

        Args:
            text (str): The name of the output label
        """
        widget = QLabel(text)
        widget.setAlignment(Qt.AlignRight)
        self._layout.insertWidget(index, widget)
        self.outputs.append(widget)

    @property
    def layout_size(self):
        return self._layout.sizeHint()
