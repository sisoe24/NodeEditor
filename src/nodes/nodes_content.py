
import logging
import sys

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
        def wrapper(*args, **kwargs):
            widget = args[1]
            if isinstance(widget, QWidget):
                return func(*args, **kwargs)
            LOGGER.error('Item is not a child of QObject: %s %s',
                         type(widget), widget)
            sys.exit()
        return wrapper

    @_is_widget
    def add_widget(self, widget, pos=0):
        """Add a widget into the node graphics

        A widget is not going to have any input or output sockets connected.

        Args:
            widget (any): A instance of a QWidget class.
        """
        self._layout.insertWidget(pos, widget)

    def add_input_widget(self, widget, label="", pos=0):
        """Add an input widget with a socket.

        Args:
            widget (any): A instance of a QWidget class.
        """
        self.inputs.append(widget)

        if label:
            _form = QFormLayout()
            _form.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
            _form.setFormAlignment(Qt.AlignLeft | Qt.AlignTop)
            _form.setLabelAlignment(Qt.AlignTop)

            label = QLabel(label)
            label.setAlignment(Qt.AlignTop)

            _form.addRow(label, widget)
            self._layout.insertLayout(pos, _form)
        else:
            self._layout.insertWidget(pos, widget)

    def add_label(self, label: str, pos=0, alignment=Qt.AlignLeft):
        """Add a label into the node.

        Args:
            label (str): The name of the label.
        """
        self._layout.insertWidget(pos, QLabel(label), alignment=alignment)

    def add_input(self, label: str, pos=0):
        """Add an input socket with a label.

        Args:
            label (str): The name of the input socket label.
        """
        label = QLabel(label)
        label.setAlignment(Qt.AlignLeft)

        self._layout.insertWidget(pos, label)
        self.inputs.append(label)

    def add_output(self, label: str, pos=0):
        """Add an output widget with a socket.

        Args:
            label (str): The name of the output socket label.
        """
        label = QLabel(label)
        label.setAlignment(Qt.AlignRight)

        self._layout.insertWidget(pos, label)
        self.outputs.append(label)

    @property
    def layout_size(self):
        return self._layout.sizeHint()

    def get_output(self, index):
        return ""
