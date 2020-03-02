# This Python file uses the following encoding: utf-8
import os, sys, urllib.request, json
import PySide2.QtQml
from PySide2.QtQuick import QQuickView
from PySide2.QtCore import QStringListModel, Qt, QUrl
from PySide2.QtGui import QGuiApplication

if __name__ == "__main__":
    app = QApplication([])
    # ...
    sys.exit(app.exec_())
