# UR5-Controller-Python-SDK

A simple controller for UR5, including 3D simulation module, robot information detection module, communication module and control module, based on Python--3.6.6, qml, and vtk.

This is a beta version and may change as needed in the future.

Please run **ur_viewmodel.py** to control a physical UR5 robot.if you want to run it without a physical robot, change qmlRobotGui/main.qml SwipeView interactive:false to true.

 - When using QmlApplicationEngine() to load qml-vtk window, in the unlikely event, you will encounter the following problems: the QML window is stuck.
 - Please check if you: import pyside2, and use QmlApplicationEngine().load to load only one qml-vtk window (such as main.qml in here containing custom qmlRegisterType "import QmlVTK 1.0") .If you have to do this, plus self.createRenderer () to __ init__ function, fboitem class.Then it works but an error window, vtkoutputwindow, will be displayed.Then try to close the vtkoutputwindow (maybe call the Win32 API findwindow?)
 - Recommended solutions:
    - import PyQt5 instead of pyside2;
    - Or using QQuickView().setSource to load qml window;
    - Or load another independent general qml window before load the qml-vtk window.
![3D simulation](https://github.com/XuhengChai/UR5-Controller-Python-SDK/blob/main/gif/ur%20controller.gif)
