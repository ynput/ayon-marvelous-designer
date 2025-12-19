from qtpy import QtWidgets, QtCore, QtGui

from ayon_core import (
    resources,
    style
)
from ayon_core.tools.utils.lib import qt_app_context
from ayon_core.tools.utils import host_tools


class MDBtnToolsWidget(QtWidgets.QWidget):
    """Widget containing buttons which are clickable."""
    tool_required = QtCore.Signal(str)

    def __init__(self, parent=None):
        super(MDBtnToolsWidget, self).__init__(parent)

        load_btn = QtWidgets.QPushButton("Load...", self)
        manage_btn = QtWidgets.QPushButton("Manage...", self)
        publish_btn = QtWidgets.QPushButton("Publish...", self)
        workfile_btn = QtWidgets.QPushButton("Workfile...", self)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(load_btn, 0)
        layout.addWidget(manage_btn, 0)
        layout.addWidget(publish_btn, 0)
        layout.addWidget(workfile_btn , 0)
        layout.addStretch(1)

        load_btn.clicked.connect(self._on_load)
        manage_btn.clicked.connect(self._on_manage)
        publish_btn.clicked.connect(self._on_publish)
        workfile_btn.clicked.connect(self._on_workfile)

    def _on_load(self):
        self.tool_required.emit("loader")

    def _on_publish(self):
        self.tool_required.emit("publisher")

    def _on_manage(self):
        self.tool_required.emit("sceneinventory")

    def _on_workfile(self):
        self.tool_required.emit("workfiles")


class MDToolsDialog(QtWidgets.QDialog):
    """Dialog with tool buttons that will stay opened until user close it."""
    def __init__(self, *args, **kwargs):
        super(MDToolsDialog, self).__init__(*args, **kwargs)

        self.setWindowTitle("Ayon tools")
        icon = QtGui.QIcon(resources.get_ayon_icon_filepath())
        self.setWindowIcon(icon)

        self.setWindowFlags(
            QtCore.Qt.Window
            | QtCore.Qt.WindowStaysOnTopHint
            | QtCore.Qt.WindowMinimizeButtonHint
            | QtCore.Qt.WindowMaximizeButtonHint
            | QtCore.Qt.WindowCloseButtonHint
        )
        self.setFocusPolicy(QtCore.Qt.StrongFocus)

        tools_widget = MDBtnToolsWidget(self)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(tools_widget)

        tools_widget.tool_required.connect(self._on_tool_require)
        self._tools_widget = tools_widget

        self._first_show = True

    def sizeHint(self):
        result = super(MDToolsDialog, self).sizeHint()
        result.setWidth(result.width() * 2)
        return result

    def showEvent(self, event):
        super(MDToolsDialog, self).showEvent(event)
        if self._first_show:
            self.setStyleSheet(style.load_stylesheet())
            self._first_show = False

    def _on_tool_require(self, tool_name):
        host_tools.show_tool_by_name(tool_name, parent=self)


class WindowCache:
    """Cached objects and methods to be used in global scope."""
    dialog = None
    _popup = None
    _first_show = True

    @classmethod
    def show_dialog(cls):
        with qt_app_context():
            if cls.dialog is None:
                cls.dialog = MDToolsDialog()

            cls.dialog.show()
            cls.dialog.raise_()
            cls.dialog.activateWindow()


def show_tools_dialog():
    if not WindowCache.dialog or not WindowCache.dialog.isVisible():
        WindowCache.show_dialog()
    return WindowCache.dialog
