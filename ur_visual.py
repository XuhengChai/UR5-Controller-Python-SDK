from PySide2.QtCore import QObject, QUrl, qDebug, Slot, QFileInfo, QEvent, Qt, QSize, Signal, QPointF
from PySide2.QtGui import (QSurfaceFormat, QGuiApplication, QMouseEvent,
                           QWheelEvent, QOpenGLFramebufferObject,
                           QOpenGLFramebufferObjectFormat, QOpenGLFunctions)
from PySide2.QtQuick import QQuickFramebufferObject, QQuickView
from PySide2.QtQml import qmlRegisterType, QQmlApplicationEngine
# from PySide2.QtWidgets import QApplication

import numpy as np
import vtk
import os
import sys
import time

def abs_path(relative_path: str):
    return os.path.join(os.path.dirname(__file__), relative_path)

class FboItem(QQuickFramebufferObject):
    def __init__(self):
#        qDebug('FboItem::__init__')
        super().__init__()
        self.__fbo_renderer = None

        self.__m_lastMouseLeftButton: QMouseEvent = QMouseEvent(QEvent.Type.None_, QPointF(0, 0), Qt.NoButton,
                                                                Qt.NoButton, Qt.NoModifier)
        self.__m_lastMouseButton: QMouseEvent = QMouseEvent(QEvent.Type.None_, QPointF(0, 0), Qt.NoButton, Qt.NoButton,
                                                            Qt.NoModifier)
        self.__m_lastMouseMove: QMouseEvent = QMouseEvent(QEvent.Type.None_, QPointF(0, 0), Qt.NoButton, Qt.NoButton,
                                                          Qt.NoModifier)
        self.__m_lastMouseWheel: QWheelEvent = None

        self.setMirrorVertically(True)  # QtQuick and OpenGL have opposite Y-Axis directions
        self.setAcceptedMouseButtons(Qt.RightButton | Qt.LeftButton | Qt.MidButton) #我是智障
        # self.createRenderer()

    def createRenderer(self):
#        qDebug('FboItem::createRenderer')
        self.__fbo_renderer = FboRenderer()
        return self.__fbo_renderer

    # #* Camera related functions

    def wheelEvent(self, e: QWheelEvent):
        # print("myMouseWheel in Item...")
        self.__m_lastMouseWheel = self.__cloneMouseWheelEvent(e)
        self.__m_lastMouseWheel.ignore()
        e.accept()
        self.update()

    def mousePressEvent(self, e: QMouseEvent):
#        qDebug("mousePressEvent in Item...")
        self.__m_lastMouseButton = self.__cloneMouseEvent(e)
        self.__m_lastMouseButton.ignore()
        e.accept()
        self.update()
#        if e.buttons() & (Qt.AllButtons):


    def mouseReleaseEvent(self, e: QMouseEvent):
        # print("mouseReleaseEvent in Item...")
        self.__m_lastMouseButton = self.__cloneMouseEvent(e)
        self.__m_lastMouseButton.ignore()
        e.accept()
        self.update()
#        if e.buttons() & (Qt.AllButtons):

    def mouseMoveEvent(self, e: QMouseEvent):
        # print("mouseMoveEvent in Item...")
        self.__m_lastMouseMove = self.__cloneMouseEvent(e)
        self.__m_lastMouseMove.ignore()
        e.accept()
        self.update()
#        if e.buttons() & (Qt.AllButtons): #Qt.RightButton | Qt.LeftButton |

    def getLastMouseButton(self) -> QMouseEvent:
        return self.__m_lastMouseButton

    def getLastMoveEvent(self) -> QMouseEvent:
        return self.__m_lastMouseMove

    def getLastWheelEvent(self) -> QWheelEvent:
        return self.__m_lastMouseWheel

    @Slot()
    def resetCamera(self):
        self.__fbo_renderer.renderer.resetCamera()
        self.update()

    def __cloneMouseEvent(self, e: QMouseEvent):
        event_type = e.type()
        local_pos = e.localPos()
        button = e.button()
        buttons = e.buttons()
        modifiers = e.modifiers()
        clone = QMouseEvent(event_type, local_pos, button, buttons, modifiers)
        clone.ignore()
        return clone

    def __cloneMouseWheelEvent(self, e: QWheelEvent):
        pos = e.pos()
        globalPos = e.globalPos()
        pixelDelta = e.pixelDelta()
        angleDelta = e.angleDelta()
        buttons = e.buttons()
        modifiers = e.modifiers()
        phase = e.phase()
        inverted = e.inverted()
        clone = QWheelEvent(pos, globalPos, pixelDelta, angleDelta, buttons, modifiers, phase, inverted)
        clone.ignore() # clone.accepted = False
        # clone.accepted = False
        return clone

    def addModel(self, fileName):
        self.__fbo_renderer.addModel(fileName)
        self.update()

    # synchronize physical robot motion with simulation
    @Slot('QVariantList')
    def onJointValueRevised(self, qmllist):
        self.__fbo_renderer.renderer.update_robot_state(qmllist)
        self.update()
        # print(type(qmllist),type(self.TCP_list))

    # @Slot(float, float, int, int, int)
    # def onMousePressed( self, x: float, y: float, button: int, buttons: int, modifiers: int):
    #     qDebug('CanvasHandler::mousePressEvent()')
    #     # self.__m_lastMouseButton = QMouseEvent(
    #     #     QEvent.MouseButtonPress,
    #     #     QPointF(x, y),
    #     #     Qt.MouseButton(button),
    #     #     Qt.MouseButtons(buttons),
    #     #     Qt.KeyboardModifiers(modifiers),
    #     # )
    #     # self.__m_lastMouseButton.ignore()
    #     # self.update()
    #
    #     # self.__m_vtkFboItem.selectModel(screenX, screenY)
    #
    # @Slot(float, float, int, int, int)
    # def onMouseMove( self, x: float, y: float, button: int, buttons: int, modifiers: int):
    #     qDebug('CanvasHandler::mouseMoveEvent()')
    #     # self.__m_lastMouseMove = QMouseEvent(
    #     #     QEvent.MouseMove,
    #     #     QPointF(x, y),
    #     #     Qt.MouseButton(button),
    #     #     Qt.MouseButtons(buttons),
    #     #     Qt.KeyboardModifiers(modifiers),
    #     # )
    #     # self.__m_lastMouseMove.ignore()
    #     # self.update()
    #
    # @Slot(float, float, int, int, int)
    # def onMouseReleased(self, x: float, y: float, button: int, buttons: int, modifiers: int):
    #     qDebug('CanvasHandler::mouseReleaseEvent()')
    #     # self.__m_lastMouseButton = QMouseEvent(
    #     #     QEvent.MouseButtonRelease,
    #     #     QPointF(x, y),
    #     #     Qt.MouseButton(button),
    #     #     Qt.MouseButtons(buttons),
    #     #     Qt.KeyboardModifiers(modifiers),
    #     # )
    #     # self.__m_lastMouseButton.ignore()
    #     # print('onMouseReleased',self.__m_lastMouseButton.button(),self.__m_lastMouseButton.type())
    #     # self.update()


class FboRenderer(QQuickFramebufferObject.Renderer):
    def __init__(self):
        super().__init__()
        self.renderer = RendererHelper()
        self.__fbo = None

    def render( self ):
        self.renderer.render()

    def synchronize(self, item:QQuickFramebufferObject):
        self.renderer.synchronize(item)

    def createFramebufferObject( self, size ):
        self.__fbo = self.renderer.createFramebufferObject( size )
        return self.__fbo

    def addModel(self, fileName):
        self.renderer.addModel(fileName)

    def update_robot_state(self, pose: list):
        self.renderer.update_robot_state(pose)

class RendererHelper(QObject):

    def initilize(self):
        self._glFunc = QOpenGLFunctions()  # used in all OpenGL systems
        self._renderWindow = vtk.vtkGenericOpenGLRenderWindow() # Can not Resize
        # self._renderWindow = vtk.vtkExternalOpenGLRenderWindow()  # Recommend; vtk-8.1.2-py3-none-any.whl
        self._renderer: vtk.vtkRenderer = vtk.vtkRenderer()
        self._renderWindow.AddRenderer(self._renderer)

        # * Interactor
        self._rwInteractor = vtk.vtkGenericRenderWindowInteractor()
        self._rwInteractor.EnableRenderOff()
        self._rwInteractor.SetRenderWindow(self._renderWindow)

        # * Initialize the OpenGL context for the renderer
        self._renderWindow.OpenGLInitContext()

        # * Interactor Style
        style = vtk.vtkInteractorStyleTrackballCamera()
        style.SetDefaultRenderer(self._renderer)
        style.SetMotionFactor(10.0)
        self._rwInteractor.SetInteractorStyle(style)

        self.__m_mouseLeftButton: QMouseEvent = None
        self.__m_mouseEvent: QMouseEvent = None
        self.__m_moveEvent: QMouseEvent = None
        self.__m_wheelEvent: QWheelEvent = None
        self.__fboItem: "QmlVTKRenderWindowInteractor" = None
        self.__firstRender = True
        self.jointPose = np.array([0,0,0,0,0,0])
        self._axis = [[0,0,1],[0,1,0],[0,1,0],[0,1,0],[0,0,1],[0,1,0] ]
        self.__jointPoseChanged = False

    def __init__(self):
#        qDebug("Creating FbItemRenderer")
        super().__init__()
        self.initilize()

    def synchronize(self, item:QQuickFramebufferObject):
#        qDebug("Synchronizing")
        if not self.__fboItem:
            self.__fboItem = item
        rendererSize = self._renderWindow.GetSize()
        if self.__fboItem.width() != rendererSize[0] or self.__fboItem.height() != rendererSize[1]:
            self._renderWindow.SetSize(int(self.__fboItem.width()), int(self.__fboItem.height()))

        #* Copy mouse events
        # print(self.__fboItem.getLastMouseButton().isAccepted())
        if not self.__fboItem.getLastMouseButton().isAccepted():
            self.__m_mouseEvent = self.__fboItem.getLastMouseButton()


        if not self.__fboItem.getLastMoveEvent().isAccepted():
            self.__m_moveEvent = self.__fboItem.getLastMoveEvent()

        if self.__fboItem.getLastWheelEvent() and not self.__fboItem.getLastWheelEvent().isAccepted():
            self.__m_wheelEvent = self.__fboItem.getLastWheelEvent()


    def createFramebufferObject(self, size: QSize) -> QOpenGLFramebufferObject:
#        qDebug("Creating FrameBufferObject")
        format = QOpenGLFramebufferObjectFormat()
        format.setAttachment(QOpenGLFramebufferObject.Depth)  # or QOpenGLFramebufferObject.CombinedDepthStencil
        self.__openGLFbo = QOpenGLFramebufferObject(size, format)
        # self.__openGLFbo.release()
        return self.__openGLFbo

    def openGLInitState(self):
        self._renderWindow.OpenGLInitState()
        self._renderWindow.MakeCurrent()
        self._glFunc.initializeOpenGLFunctions()
        # self._glFunc.glUseProgram(0)

    def update_robot_state(self, pose):
        if self.__firstRender:
            return
#        self.deltaJoint = np.array(pose) - self.jointPose
#        print(np.round(self.deltaJoint,2))
        self.jointPose = np.array(pose)
        self.__jointPoseChanged = True

    def render(self):
        self._renderWindow.PushState()
        self.openGLInitState()
        self._renderWindow.Start()

        # the first time to Render, add all model. after that, use self.update
        if self.__firstRender:
            # self.renderWindow.SetOffScreenRendering(True)
            self.sceneur = URVtk()
            # time.sleep(0.1)
            # print(sceneur.ur_assembly)
            self._renderer.AddActor(self.sceneur.ur_assembly[0])
            self._renderer.AddActor(self.sceneur.groundSence)
            self._renderer.AddActor(self.sceneur.axesSence)
            self.resetCamera()
            self.__firstRender = False
        else:
            if self.__jointPoseChanged:
                self.sceneur.ur_assembly[1].SetOrientation(0, 0, self.jointPose[0])
                self.sceneur.ur_assembly[2].SetOrientation(0, 90+self.jointPose[1], 0)
                self.sceneur.ur_assembly[3].SetOrientation(0, self.jointPose[2], 0)
                self.sceneur.ur_assembly[4].SetOrientation(0, 90+self.jointPose[3], 0)
                self.sceneur.ur_assembly[5].SetOrientation(0, 0, self.jointPose[4])
                self.sceneur.ur_assembly[6].SetOrientation(0, self.jointPose[5], 0)
                self.__jointPoseChanged = False

        #* Process camera related commands
        if self.__m_mouseEvent and not self.__m_mouseEvent.isAccepted():
            self._rwInteractor.SetEventInformationFlipY(
                self.__m_mouseEvent.x(), self.__m_mouseEvent.y(),
                1 if (self.__m_mouseEvent.modifiers() & Qt.ControlModifier) > 0 else 0,
                1 if (self.__m_mouseEvent.modifiers() & Qt.ShiftModifier) > 0 else 0,
                '0',
                1 if self.__m_mouseEvent.type() == QEvent.MouseButtonDblClick else 0,
                None
            )
            if self.__m_mouseEvent.type() == QEvent.MouseButtonPress:
                if self.__m_mouseEvent.button() == Qt.LeftButton:
                    self._rwInteractor.LeftButtonPressEvent()
                elif self.__m_mouseEvent.button() == Qt.RightButton:
                    self._rwInteractor.RightButtonPressEvent()
                elif self.__m_mouseEvent.button() == Qt.MidButton:
                    self._rwInteractor.MiddleButtonPressEvent()
                # self._rwInteractor.InvokeEvent(vtk.vtkCommand.LeftButtonPressEvent)
            elif self.__m_mouseEvent.type() == QEvent.MouseButtonRelease:
                if self.__m_mouseEvent.button() == Qt.LeftButton:
                    self._rwInteractor.LeftButtonReleaseEvent()
                elif self.__m_mouseEvent.button() == Qt.RightButton:
                    self._rwInteractor.RightButtonReleaseEvent()
                elif self.__m_mouseEvent.button() == Qt.MidButton:
                    self._rwInteractor.MiddleButtonReleaseEvent()
                # self._rwInteractor.InvokeEvent(vtk.vtkCommand.LeftButtonReleaseEvent)
            self.__m_mouseEvent.accept()

        #* Process move event
        if self.__m_moveEvent and not self.__m_moveEvent.isAccepted():
            if self.__m_moveEvent.type() == QEvent.MouseMove and self.__m_moveEvent.buttons() & (Qt.RightButton | Qt.LeftButton | Qt.MidButton) :
                self._rwInteractor.SetEventInformationFlipY(
                    self.__m_moveEvent.x(),
                    self.__m_moveEvent.y(),
                    1 if (self.__m_moveEvent.modifiers() & Qt.ControlModifier) > 0 else 0,
                    1 if (self.__m_moveEvent.modifiers() & Qt.ShiftModifier) > 0 else 0,
                    '0',
                    1 if self.__m_moveEvent.type() == QEvent.MouseButtonDblClick else 0
                )
                self._rwInteractor.InvokeEvent(vtk.vtkCommand.MouseMoveEvent)

            self.__m_moveEvent.accept()

        #* Process wheel event
        if self.__m_wheelEvent and not self.__m_wheelEvent.isAccepted():
            self._rwInteractor.SetEventInformationFlipY(
                self.__m_wheelEvent.x(), self.__m_wheelEvent.y(),
                1 if (self.__m_wheelEvent.modifiers() & Qt.ControlModifier) > 0 else 0,
                1 if (self.__m_wheelEvent.modifiers() & Qt.ShiftModifier) > 0 else 0,
                '0',
                1 if self.__m_wheelEvent.type() == QEvent.MouseButtonDblClick else 0
            )
            if self.__m_wheelEvent.delta() > 0:
                self._rwInteractor.InvokeEvent(vtk.vtkCommand.MouseWheelForwardEvent)
            elif self.__m_wheelEvent.delta() < 0:
                self._rwInteractor.InvokeEvent(vtk.vtkCommand.MouseWheelBackwardEvent)

            self.__m_wheelEvent.accept()


        # Render
        self._renderWindow.Render()
        self._renderWindow.PopState()
        self.__fboItem.window().resetOpenGLState()

    def addModel(self, fileName):
        reader = vtk.vtkSTLReader()
        url = QUrl(fileName)
        reader.SetFileName(url.path())
        reader.Update()

        transform = vtk.vtkTransform()
        transform.Scale( (.5,.5,.5) )

        transformFilter = vtk.vtkTransformPolyDataFilter()
        transformFilter.SetInputConnection(reader.GetOutputPort())
        transformFilter.SetTransform(transform)
        transformFilter.Update()

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(transformFilter.GetOutputPort())

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        self.renderer.AddActor(actor)

        print(f"Added...{url.path()}")

    def resetCamera(self):
        self._renderer.SetBackground(1.0, 1.0, 1.0)
        self._renderer.SetBackground2(0.529, 0.8078, 0.92157)
        # self._renderer.SetBackground2(0.67, 0.67, 0.67)
        self._renderer.GradientBackgroundOn()
        #  设置相机参数
        # Seting the clipping range here messes with the opacity of the actors prior to moving the camera
        # self._ren.GetActiveCamera().Yaw(90)  #鼠标向左转动，顺时针
        # self._ren.GetActiveCamera().Pitch(25)  #鼠标向上转动，顺时针
        # self._ren.GetActiveCamera().Roll(-90) #垂直于屏幕的方向
        # self._ren.ResetCamera()
        m_camPositionX = -2
        m_camPositionY = -2
        m_camPositionZ = 2
        self._renderer.GetActiveCamera().SetPosition(m_camPositionX, m_camPositionY, m_camPositionZ)
        self._renderer.GetActiveCamera().SetFocalPoint(0.2, 0.2, 0.0)
        self._renderer.GetActiveCamera().SetViewUp(0.0, 0.0, 1.0)
        self._renderer.ResetCameraClippingRange()

# class MyInteractorStyle(vtk.vtkInteractorStyleTrackballCamera):
#
#     def __init__(self,parent=None):
#         self.AddObserver("MiddleButtonPressEvent",self.middleButtonPressEvent)
#         self.AddObserver("MiddleButtonReleaseEvent",self.middleButtonReleaseEvent)
#
#     def middleButtonPressEvent(self,obj,event):
#         print("Middle Button pressed")
#         self.OnMiddleButtonDown()
#         return
#
#     def middleButtonReleaseEvent(self,obj,event):
#         print("Middle Button released")
#         self.OnMiddleButtonUp()
#         return
class MyInteractor(vtk.vtkInteractorStyleTrackballCamera):
    def __init__(self, assembly, dt, renWin, parent=None):
        self.AddObserver("CharEvent", self.OnCharEvent)
        self.AddObserver("KeyPressEvent", self.OnKeyPressEvent)
        self.assembly = assembly
        self.dt = dt
        self.renWin = renWin

    # Override the default key operations which currently handle trackball or joystick styles is provided
    # OnChar is triggered when an ASCII key is pressed. Some basic key presses are handled here
    def OnCharEvent(self, obj, event):
        pass

    def OnKeyPressEvent(self, obj, event):
        # global angle
        # Get the compound key strokes for the event
        key = self.GetInteractor().GetKeySym()
        # Output the key that was pressed
        # print "Pressed: " , key
        # Handle an arrow key
        if (key == "Left"):
            self.assembly[1].RotateZ(-self.dt)
        if (key == "Right"):
            self.assembly[1].RotateZ(self.dt)
        if (key == "Up"):
            self.assembly[0].RotateZ(-self.dt)
            # angle[0] += self.dt
            # if angle[0] >= 360.0:
            #     angle[0] -= 360.0
        if (key == "Down"):
            self.assembly[0].RotateZ(self.dt)
            # angle[0] -= self.dt
            # if angle[0] < 0.0:
            #     angle[0] += 360.0
        # Ask each renderer owned by this RenderWindow to render its image and synchronize this process
        self.renWin.Render()
        return

#
class URVtk():
    # process: vtkActor------vtkRenderer------vtkRenderWindow------vtkRenderWindowInteractor
    def __init__(self):
        self.set_filename()
        self.ur_assembly = self.get_assembly()
        self.groundSence = self.createGround()
        self.axesSence = self.createCoordinates()

    def set_win(self):
        # 显示渲染窗口
        self._RenderWindow = vtk.vtkRenderWindow()  # 将操作系统与VTK渲染引擎连接到一起。
        self._RenderWindow.SetSize(450, 450)
        self._RenderWindow.AddRenderer(self.get_render())
        # 创建交互控键（可以用鼠标拖来拖去看三维模型）
        self._Iren = vtk.vtkRenderWindowInteractor()
        self._Iren.SetRenderWindow(self._RenderWindow)
        # style = vtk.vtkInteractorStyleTrackballCamera()
        style = MyInteractor(self.ur_assembly, 10, self._RenderWindow)
        self._Iren.SetInteractorStyle(style)
        # self.ur_assembly[0].RotateZ(90)
        self._Iren.Initialize()
        self._Iren.Start()
    def get_render(self):
        # 渲染（将执行单元和背景组合在一起按照某个视角绘制）
        self._ren = vtk.vtkRenderer()
        # ur_assemble = self.ur_assembly[0]
        self._ren.AddActor(self.ur_assembly[0])
        self._ren.SetBackground(1.0, 1.0, 1.0)
        self._ren.SetBackground2(0.529, 0.8078, 0.92157)
        # self._ren.SetBackground2(0.67, 0.67, 0.67)
        self._ren.GradientBackgroundOn()

        #  设置相机参数
        # self._ren.GetActiveCamera().Yaw(90)  #鼠标向左转动，顺时针
        # self._ren.GetActiveCamera().Pitch(25)  #鼠标向上转动，顺时针
        # self._ren.GetActiveCamera().Roll(-90) #垂直于屏幕的方向
        # self._ren.ResetCamera()
        m_camPositionX = -5
        m_camPositionY = -5
        m_camPositionZ = 5
        self._ren.GetActiveCamera().SetPosition(m_camPositionX, m_camPositionY, m_camPositionZ)
        self._ren.GetActiveCamera().SetFocalPoint(0.0, 0.0, 0.0)
        self._ren.GetActiveCamera().SetViewUp(0.0, 0.0, 1.0)
        self._ren.ResetCameraClippingRange()

        self._ren.AddActor(self.createGround())
        self._ren.AddActor(self.createCoordinates())
        return self._ren

    def set_filename(self):
        # self.filenames = [r"ur5_stl\base.stl", r"ur5_stl\shoulder.stl", r"ur5_stl\upperarm.stl",
        #              r"ur5_stl\forearm.stl", r"ur5_stl\wrist1.stl", r"ur5_stl\wrist2.stl",
        #              r"ur5_stl\wrist3.stl"]
        # self.filenames = [r"ur5_obj\base.obj", r"ur5_obj\shoulder.obj", r"ur5_obj\upperarm.obj",
        #              r"ur5_obj\forearm.obj", r"ur5_obj\wrist1.obj", r"ur5_obj\wrist2.obj",
        #              r"ur5_obj\wrist3.obj"]

        self.filenames = [r"ur5_ply\base.ply", r"ur5_ply\shoulder.ply", r"ur5_ply\upperarm.ply",
                     r"ur5_ply\forearm.ply", r"ur5_ply\wrist1.ply", r"ur5_ply\wrist2.ply",
                     r"ur5_ply\wrist3.ply"]
        # pose = [[0, 0, 0,            0, 0, 0],
        #         [0, 0, 0.089159,     0, 0, 0],
        #         [0, 0.13585, 0,      0, np.pi/2, 0],
        #         [0, 0.1197, 0.42500, 0,0,0],
        #         [0, 0, 0.39225,      0,np.pi/2,0],
        #         [0, 0.093, 0,        0,0,0],
        #         [0, 0.09465 , 0,     0,0,0],
        #         [0, 0.0823, 0,       0,0,math.pi/2],
        #         ]
        self.pose = [[0, 0, 0, 0, 0, 0],
                [0, 0, 0.089159, 0, 0, 0],
                [0, 0.13585, 0.089159, 0, np.pi / 2, 0],
                [0, 0.01615, 0.514159, 0, 0, 0],
                [0, 0.01615, 0.906409, 0, np.pi / 2, 0],
                [0, 0.10915, 0.906409, 0, 0, 0],
                [0, 0.10915, 1.001059, 0, 0, 0],  # wrist3 mounted position
                # [0, 0.19145, 1.001059,       0,0,math.pi/2], # TCP position
                ]

    def get_assembly(self):
        actor = list()  # the list of links
        ur_assembly = [vtk.vtkAssembly()]
        for id, file in enumerate(self.filenames):
            actor.append(self.get_polydata_actor(file, self.pose[id][0:3]))
            self.set_actor_property(actor[id],id)
            # 装配体添加零件
            ur_assembly[id].AddPart(actor[id])
            if id < len(self.filenames):
                assembly = vtk.vtkAssembly()
                ur_assembly.append(assembly)
                ur_assembly[id].AddPart(ur_assembly[id + 1])
            ur_assembly[id].SetOrigin(self.pose[id][0], self.pose[id][1], self.pose[id][2])
        # for id, assembe in enumerate(ur_assembly):
        #     ur_assembly[id].Rotate()
#        initialize_pose = [45, 45, 45, 45, 45, 30]
        initialize_pose = [0, 0, 0, 0, 0, 0]

        ur_assembly[1].SetOrientation(0, 0, initialize_pose[0])
        ur_assembly[2].SetOrientation(0, 90+initialize_pose[1], 0)
        ur_assembly[3].SetOrientation(0, initialize_pose[2], 0)
        ur_assembly[4].SetOrientation(0, 90+initialize_pose[3], 0)
        ur_assembly[5].SetOrientation(0, 0, initialize_pose[4])
        ur_assembly[6].SetOrientation(0, initialize_pose[5], 0)
#        ur_assembly[1].RotateZ(initialize_pose[0])
#        ur_assembly[2].RotateY(initialize_pose[1])
#        ur_assembly[3].RotateY(initialize_pose[2])
#        ur_assembly[4].RotateY(initialize_pose[3])
#        ur_assembly[5].RotateZ(initialize_pose[4])
#        ur_assembly[6].RotateY(initialize_pose[5])

        # ur_assembly[0].RotateX(180)
        ur_assembly[0].RotateZ(-90)
        return ur_assembly

    def get_polydata_actor(self, filename, pose):
        # reader = vtk.vtkSTLReader()
        # reader = vtk.vtkOBJReader()
        reader = vtk.vtkPLYReader()
        reader.SetFileName(abs_path(filename))
        reader.Update()
        # print('Ply',reader)
        transform = vtk.vtkTransform()
        transform.Translate(pose[0], pose[1], pose[2])

        transformFilter = vtk.vtkTransformPolyDataFilter()
        transformFilter.SetInputConnection(reader.GetOutputPort())
        transformFilter.SetTransform(transform)
        transformFilter.Update()

        mapper = vtk.vtkPolyDataMapper()  # maps polygonal data to graphics primitives
        mapper.SetInputConnection(transformFilter.GetOutputPort())
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        return actor  # represents an entity in a rendered scene

    def set_actor_property(self, actor, id):
        # actor[id].GetProperty().SetColor(0.3,0.3,0.3)
        # r = vtk.vtkMath.Random(.4, 1.0)
        # g = vtk.vtkMath.Random(.4, 1.0)
        # b = vtk.vtkMath.Random(.4, 1.0)
        rgb =[[0.41 , 0.89 , 0.61], [0.9 , 0.44 , 0.83], [0.62 , 0.41 , 0.72],
        [0.48 , 0.63 , 0.61], [0.43 , 0.81 , 0.95], [0.67 , 0.97 , 0.44], [0.67 , 0.97 , 0.44]]
        actor.GetProperty().SetAmbientColor(rgb[id][0], rgb[id][1], rgb[id][2])
        # # 漫反射
        actor.GetProperty().SetDiffuseColor(rgb[id][0], rgb[id][1], rgb[id][2])
        actor.GetProperty().SetDiffuse(.8)
        # 镜面反射
        actor.GetProperty().SetSpecular(.5)
        actor.GetProperty().SetSpecularColor(0.7, 0.7, 0.7)
        actor.GetProperty().SetSpecularPower(30.0)
        # actor.GetProperty().SetOpacity(0.1)

    def createGround(self):
        # create plane source
        plane = vtk.vtkPlaneSource()
        plane.SetXResolution(10)
        plane.SetYResolution(10)
        # plane.SetZResolution(10)
        plane.SetCenter(0, 0, 0)
        plane.SetNormal(0, 0, 1)
        # mapper
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(plane.GetOutputPort())

        # actor
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetRepresentationToWireframe()
        # actor.GetProperty().SetOpacity(0.4) # 1.0 is totally opaque and 0.0 is completely transparent
        actor.GetProperty().SetColor(0.8, 0.8, 0.8)
        '''
        # Load in the texture map. A texture is any unsigned char image.
        bmpReader = vtk.vtkBMPReader()
        bmpReader.SetFileName("ground_texture.bmp")
        texture = vtk.vtkTexture()
        texture.SetInputConnection(bmpReader.GetOutputPort())
        texture.InterpolateOn()
        actor.SetTexture(texture)
        '''
        transform = vtk.vtkTransform()
        transform.Scale(3, 3, 1)
        actor.SetUserTransform(transform)
        return actor

    def createCoordinates(self):
        # create coordinate axes in the render window
        axes = vtk.vtkAxesActor()
        axes.SetTotalLength(2, 2, 2)  # Set the total length of the axes in 3 dimensions
        # Set the type of the shaft to a cylinder:0, line:1, or user defined geometry.
        axes.SetShaftType(1)
        # axes.SetCylinderRadius(0.01)
        axes_label_font_size = 20
        # axes.GetXAxisCaptionActor2D().SetWidth(0.02)
        # axes.GetYAxisCaptionActor2D().SetWidth(0.02)
        # axes.GetZAxisCaptionActor2D().SetWidth(0.02)
        axes.GetXAxisCaptionActor2D().GetTextActor().SetTextScaleModeToNone()
        axes.GetYAxisCaptionActor2D().GetTextActor().SetTextScaleModeToNone()
        axes.GetZAxisCaptionActor2D().GetTextActor().SetTextScaleModeToNone()
        axes.GetXAxisCaptionActor2D().GetCaptionTextProperty().SetFontSize(axes_label_font_size)
        axes.GetYAxisCaptionActor2D().GetCaptionTextProperty().SetFontSize(axes_label_font_size)
        axes.GetZAxisCaptionActor2D().GetCaptionTextProperty().SetFontSize(axes_label_font_size)
        # axes.SetAxisLabels(1) # Enable:1/disable:0 drawing the axis labels
        # transform = vtk.vtkTransform()
        # transform.Translate(0.0, 0.0, 0.0)
        # axes.SetUserTransform(transform)
        # axes.GetXAxisCaptionActor2D().GetCaptionTextProperty().SetColor(1,0,0)
        # axes.GetXAxisCaptionActor2D().GetCaptionTextProperty().BoldOff() # disable text bolding
        return axes

class utils():
    def defaultFormat(stereo_capable):
        fmt = QSurfaceFormat()
        fmt.setRenderableType(QSurfaceFormat.OpenGL)
        fmt.setVersion(3, 2)
        fmt.setProfile(QSurfaceFormat.CoreProfile)
        fmt.setSwapBehavior(QSurfaceFormat.DoubleBuffer)
        fmt.setRedBufferSize(8)
        fmt.setGreenBufferSize(8)
        fmt.setBlueBufferSize(8)
        fmt.setDepthBufferSize(8)
        fmt.setAlphaBufferSize(8)
        fmt.setStencilBufferSize(0)
        fmt.setStereo(stereo_capable)
        fmt.setSamples(0)
        return fmt

    def setup_vtk_log(log_file: str = "vtk.log", append: bool = False):
        fow = vtk.vtkFileOutputWindow()
        fow.SetFileName(os.path.join(os.path.dirname(__file__), log_file))
        fow.SetAppend(append)
        ow = vtk.vtkOutputWindow()
        ow.SetInstance(fow)

def main():
    # QApplication.setAttribute( Qt.AA_UseDesktopOpenGL )
    # QSurfaceFormat.setDefaultFormat(utils.defaultFormat(False)) # from vtk 8.2.0
    app = QGuiApplication(sys.argv)
    app.setApplicationName('QtVTK-Py')
    # qmlRegisterType(FboItem, "QmlVTK", 1, 0, "Interactor")
    qmlRegisterType(FboItem, "QtVTK", 1, 0, "VtkFboItem")

    view = QQuickView()  # qml file must begin with Item, not ApplicationWindow
    view.setSource(QUrl.fromLocalFile(abs_path("main.qml")))
    # view.setTitle ("QQuickView Load")
    # view.setResizeMode(QQuickView.SizeRootObjectToView)
#    view.setFlags(Qt.FramelessWindowHint)
    view.show()

    '''
    In the unlikely event, you will encounter the following problems: the QML window is stuck.

    Please check if you: import pyside2, and use QmlApplicationEngine().load to load only one qml-vtk window(containing qmlRegisterType class) .
    If you have to do this, plus self.createRenderer () to __ init__ function, fboitem class.
    Then it works but an error window, vtkoutputwindow, will be displayed.
    Then try to close the vtkoutputwindow (maybe call the Win32 API findwindow?)

    Recommended solution: import PyQt5 instead of pyside2;
    Or using QQuickView().setSource to load qml window;
    Or load another independent general qml window before load the qml-vtk window.

    '''
#    engine1 = QQmlApplicationEngine()  # qml file must begin with ApplicationWindow, not Item
#    engine1.load(os.path.join(os.path.dirname(__file__), "main.qml")) # another independent general qml window

#    engine = QQmlApplicationEngine()
#    engine.load(os.path.join(os.path.dirname(__file__), "app.qml"))  # the qml-vtk window
#    if not engine.rootObjects():
#        sys.exit(-1)

    sys.exit(app.exec_())

if __name__ == '__main__':
    # a = URVtk()
    # a.set_win()
    main()

