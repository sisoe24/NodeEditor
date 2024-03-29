import logging

from collections import namedtuple

from PySide2.QtCore import Qt
from PySide2.QtWidgets import (
    QCheckBox,
    QFormLayout,
    QSpacerItem,
    QLabel,
    QVBoxLayout,
    QWidget
)

from src.widgets.node_socket import SocketType

LOGGER = logging.getLogger('nodeeditor.master_node')

SocketData = namedtuple('SocketData', ['data', 'widget', 'label'])


class NodeContent(QWidget):

    def __init__(self, node, parent=None):
        super().__init__(parent)

        self.node = node

        self.inputs = []
        self.outputs = []

        self.widgets = {}
        self._replaceable_widgets = {}

        self._layout = QVBoxLayout()
        self._layout.setContentsMargins(10, 10, 10, 10)
        self._layout.addSpacerItem(QSpacerItem(0, 0))
        self._layout.setSpacing(15)
        self.setLayout(self._layout)

    @property
    def layout_size(self):
        return self._layout.sizeHint()

    def add_widget(self, widget, pos=0):
        """Add a widget into the node graphics

        A widget is not going to have any input or output sockets connected.

        Args:
            widget (any): A instance of a QWidget class.
        """
        self._layout.insertWidget(pos, widget)

    def add_label(self, label: str, pos=0, alignment=Qt.AlignLeft):
        """Add a label into the node.

        Args:
            label (str): The name of the label.
        """
        label = QLabel(label)
        self._layout.insertWidget(pos, label, alignment=alignment)
        return label

    def _add_input(self, socket_type, label, pos):
        """Add an input socket with a label.

        Args:
            label (str): The name of the input socket label.
        """
        label.setAlignment(Qt.AlignLeft)
        self._layout.insertWidget(pos, label)
        self.inputs.append(SocketData(socket_type, label, label.text()))

    def add_input_widget(self, widget, label="", pos=0, socket_type: SocketType = None):
        """Add an input widget with a socket.

        Args:
            widget (any): A instance of a QWidget class.
        """
        socket_type = socket_type or SocketType.widget
        self.inputs.append(SocketData(socket_type, widget, label))

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

    def add_input(self, socket_type: SocketType, label: str, pos=0):
        """Add an input socket with a label.

        Args:
            label (str): The name of the input socket label.
        """
        self._add_input(socket_type, QLabel(label), pos)

    def add_input_execute(self, label='Execute', pos=0):
        """Add an input socket with a label.

        Args:
            label (str): The name of the input socket label.
        """
        self._add_input(SocketType.execute, QLabel(label), pos)

    def add_input_list(self, label, pos=0):
        """Add an input socket with a label.

        Args:
            label (str): The name of the input socket label.
        """
        self._add_input(SocketType.array, QLabel(label), pos)

    def add_input_boolean(self, label, pos=0):
        """Add an input socket with a label.

        Args:
            label (str): The name of the input socket label.
        """
        checkbox = QCheckBox(label)
        checkbox.setObjectName(label)
        self.add_input_widget(
            checkbox, pos=pos, socket_type=SocketType.boolean)
        return checkbox

    def _add_output(self, socket_type: SocketType, label, pos):
        """Add an output widget with a socket.

        Args:
            label (str): The name of the output socket label.
        """
        label.setAlignment(Qt.AlignRight)

        self._layout.insertWidget(pos, label)
        self.outputs.append(SocketData(socket_type, label, label.text()))

    def add_output(self, socket_type: SocketType, label: str, pos=0):
        """Add an output widget with a socket.

        Args:
            label (str): The name of the output socket label.
        """
        self._add_output(socket_type, QLabel(label), pos)

    def add_output_execute(self, label='Execute', pos=0):
        """Add an input socket with a label.

        Args:
            label (str): The name of the input socket label.
        """
        self._add_output(SocketType.execute, QLabel(label), pos)

    def clear_output(self, index):
        raise NotImplementedError(self.node)

    def get_output(self, index):
        raise NotImplementedError(self.node)

    def set_input(self, value, index):
        raise NotImplementedError(self.node)

    def save_state(self):
        return {}

    def restore_state(self, content):
        pass

    def get_execute_flow(self, socket_outputs):
        if len(socket_outputs) >= 2:
            raise NotImplementedError(
                'Node should override the execute method '
                'because it has more than one exec output')
        return socket_outputs[0]

    def convert_to_label(self, index):
        socket = self.inputs[index]

        widget = socket.widget
        replaceable_widget = self._replaceable_widgets.get(widget)
        if replaceable_widget and replaceable_widget.get('replace'):
            if replaceable_widget.get('label'):
                widget.setHidden(True)
            else:
                self._convert_to_label(widget)

    def _convert_to_label(self, widget):
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
