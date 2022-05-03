import sys
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
        self.widgets = {}
        self._replaceable_widgets = {}

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

        is_form_layout = None
        if label:
            form = QFormLayout()
            form.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
            form.setFormAlignment(Qt.AlignLeft | Qt.AlignTop)
            form.setLabelAlignment(Qt.AlignTop)

            label = QLabel(label)
            label.setAlignment(Qt.AlignTop)

            form.addRow(label, widget)
            self._layout.insertLayout(pos, form)
            is_form_layout = True
        else:
            self._layout.insertWidget(pos, widget)

        self.widgets[widget] = pos
        self._replaceable_widgets[widget] = {
            'label': label, 'replace': True, 'is_form_layout': is_form_layout}

    def add_label(self, label: str, pos=0, alignment=Qt.AlignLeft):
        """Add a label into the node.

        Args:
            label (str): The name of the label.
        """
        label = QLabel(label)
        self._layout.insertWidget(pos, label, alignment)
        return label

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

    def set_input(self, value, index):
        widget = self.inputs[index]

        replaceable_widget = self._replaceable_widgets.get(widget)
        if replaceable_widget and replaceable_widget.get('replace'):
            if replaceable_widget.get('label'):
                widget.setHidden(True)
            else:
                self.convert_to_label(widget)

    def convert_to_label(self, widget):
        widget.setHidden(True)

        label = self.add_label(widget.objectName(), pos=self.widgets[widget])
        self._replaceable_widgets[widget] = {'label': label, 'replace': False}

    def restore_widget(self, widget):
        if isinstance(widget, QLabel):
            return

        replaceable_widget = self._replaceable_widgets.get(widget)

        if not replaceable_widget.get('is_form_layout'):
            label = self._replaceable_widgets[widget]['label']
            self._layout.removeWidget(label)
            label.close()
            self._replaceable_widgets[widget] = {'replace': True}

        widget.setHidden(False)
