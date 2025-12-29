"""Ayon Marvelous Designer tools dialog module."""
from __future__ import annotations

from typing import Any

from ayon_core import resources, style
from ayon_core.tools.utils import host_tools
from ayon_core.tools.utils.lib import qt_app_context
from qtpy import QtCore, QtGui, QtWidgets


class MDBtnToolsWidget(QtWidgets.QWidget):
    """Widget containing buttons which are clickable."""
    tool_required = QtCore.Signal(str)

    def __init__(self, parent=None):  # noqa: ANN001
        """Ayon Marvelous Designer tools widget.

        Args:
            parent (QMainWindow, optional): Parent widget. Defaults to None.
        """
        super(MDBtnToolsWidget, self).__init__(parent)  # noqa: UP008

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

    def _on_load(self) -> None:
        self.tool_required.emit("loader")

    def _on_publish(self) -> None:
        self.tool_required.emit("publisher")

    def _on_manage(self) -> None:
        self.tool_required.emit("sceneinventory")

    def _on_workfile(self) -> None:
        self.tool_required.emit("workfiles")


class MDToolsDialog(QtWidgets.QDialog):
    """Dialog with tool buttons that will stay opened until user close it."""
    def __init__(self, *args: Any, **kwargs: Any):
        """Ayon Marvelous Designer tools dialog."""
        super(MDToolsDialog, self).__init__(*args, **kwargs)  # noqa: UP008

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

    def sizeHint(self) -> QtCore.QSize:  # noqa: N802
        """Override size hint to make dialog wider.

        Returns:
            QSize: Size hint object with modified width.
        """
        result = super().sizeHint()
        result.setWidth(result.width() * 2)
        return result

    def showEvent(self, event: QtGui.QShowEvent) -> None:  # noqa: N802
        """Handle show event for the dialog.
        
        Applies stylesheet on first show to ensure proper styling.
        
        Args:
            event: The show event from Qt framework.
        """
        super().showEvent(event)
        if self._first_show:
            self.setStyleSheet(style.load_stylesheet())
            self._first_show = False

    def _on_tool_require(self, tool_name: str) -> None:
        host_tools.show_tool_by_name(tool_name, parent=self)


class WindowCache:
    """Cached objects and methods to be used in global scope."""
    dialog: MDToolsDialog | None = None
    _popup = None
    _first_show = True

    @classmethod
    def show_dialog(cls) -> None:
        """Show the tools dialog window.
        
        Creates a new dialog instance if none exists, then shows, raises,
        and activates the dialog window.
        """
        with qt_app_context():
            if cls.dialog is None:
                cls.dialog = MDToolsDialog()

            cls.dialog.show()
            cls.dialog.raise_()
            cls.dialog.activateWindow()


def show_tools_dialog() -> None:
    """Show the Marvelous Designer tools dialog.

    Creates and shows the tools dialog if it doesn't exist or isn't visible.
    The dialog provides access to Ayon tools like loader, publisher, scene
    inventory, and workfiles management.
    """
    if not WindowCache.dialog or not WindowCache.dialog.isVisible():
        WindowCache.show_dialog()
