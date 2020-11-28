import QtQuick 2.13
import QtQuick.Window 2.13
import QtQuick.Controls 2.3
import QtQuick.Controls.Material 2.0
//import QtQuick.Controls.impl 2.13
import QtQuick.Layouts 1.3
//import QtQuick.Controls 1.4
import QmlVTK 1.0

//Window  Item
Item {
    id: mainWindow
    visible: true
    width: 1320
    height: 700
//    title: qsTr("UR Controller")
//    onClosing: {
//            console.log("OnClosing fired");
//        }


    SwipeView {
        objectName: "swipeView"
        id: swipeView
//        currentIndex: 1
        anchors.fill: parent
        property int pointSize: 12
//        interactive:false
        interactive:true

        PageConnect {
            id: page1
            width: mainWindow.width
            height: mainWindow.height
        }

        Rectangle {
            id: page2
            implicitWidth: mainWindow.width
            implicitHeight: mainWindow.height
            color: "#f0f0f0"
            Row{
                id: row
                x: 27
                y: 22
                Label {
                    objectName: "lable_UR"
                    id: lable_UR
                    width: 250
                    text: qsTr("Universal Robot")
                    font.pixelSize: 28
                    color: "#c110ea"
                    font.bold: true
                    font.family: "Arial"
                    height: 60
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
                ColorButton {
                    id: colorButton
                    anchors.verticalCenter: parent.verticalCenter
                    height: 30
                    objectName: "disconnectButton"
                    text: "Disconnected"
                    width: 120
                }
            }

            Pane {
                objectName: "pane_simulation"
                id: pane_simulation
                x: 13
                y: 88
                width: 400
                height: 300
                rightPadding: 0
                bottomPadding: 0
                leftPadding: 0
                topPadding: 0
                contentWidth: 2
                VtkFboItem {
                    id: interactor
                    objectName: "interactor"
                    anchors.fill: parent

                    Connections{
                        target: joint_control
                        onJointposeChanged:{
                            interactor.onJointValueRevised(joint_control.jointpose)
//                            console.log("组件点击信号发出")
                        }
                    }

                    MouseArea {
                        acceptedButtons: Qt.AllButtons
                        anchors.fill: parent
        //                scrollGestureEnabled: false

                        onPositionChanged: (mouse) => {
                            //this.parent.onMouseMove(mouse.x, mouse.y, mouse.button,mouse.buttons, mouse.modifiers);
                           mouse.accepted = false;
                        }
                        onPressed: (mouse) => {
                            //this.parent.onMousePressed(mouse.x, mouse.y, mouse.button, mouse.buttons, mouse.modifiers);
                            mouse.accepted = false;
                            // if u want to propagate the pressed event
                            // so the VtkFboItem instance can receive it
                            // then uncomment the belowed line
                            // mouse.ignore() // or mouse.accepted = false
                        }
                        onReleased: (mouse) => {
                            //this.parent.onMousePressed(mouse.x, mouse.y, mouse.button, mouse.buttons, mouse.modifiers);
                            //print(mouse);
                            mouse.accepted = false;
                        }
                        onWheel: (wheel) => {
                            wheel.accepted = false;
                        }
                    }

                }
                ColorButton {
                    objectName: "reset"
                    id: button_reset
                    width: 50
                    height: 25
                    text: "Reset"
                    anchors.bottom: parent.bottom
                    anchors.bottomMargin: 0
                    anchors.right: parent.right
                    anchors.rightMargin: 0
                    font.pointSize: 10
                    onClicked: {
                        interactor.resetCamera()
//                        for (var i = 0; i < joint_control.count; ++i) {
//                            joint_control.itemAt(i).value = 0
//                        }
                    }
                }
                //                Text {
//                    text: "Reserve for Simulation"
//                    anchors.horizontalCenter: parent.horizontalCenter
//                    anchors.verticalCenter: parent.verticalCenter
//                     font.family: "Helvetica"
//                     font.pointSize: 24
//                     color: "LightGray"
//                }
            }
            Rectangle {
                x: 429
                y: 72
                id: rect_joint_all
                height: column_joint_all.height+10
                width:  column_joint_all.width+10
                border.color: "#bdbebf"
                border.width: 1
                radius: 15
                Column{
                    anchors.horizontalCenter: rect_joint_all.horizontalCenter
                    anchors.verticalCenter: rect_joint_all.verticalCenter
                    id: column_joint_all
                    spacing: 10
                    // Joint name and refresh switch
                    Row {
                        anchors.horizontalCenter: column_joint_all.horizontalCenter
                        id: row_joint_name
                        spacing: 5
                        Label {
                           anchors.verticalCenter: row_joint_name.verticalCenter
                           id: label_joint_control
                           width: 120
                           height: 30
                           color: "#5d0909"
                           text: qsTr("Joint Control")
                           font.pointSize: swipeView.pointSize
                           font.family: "Arial"
                           horizontalAlignment: Text.AlignHCenter
                           verticalAlignment: Text.AlignVCenter
                       }
                       ColorButton {
                           objectName: "moveJointButton"
                           id: button_move_joint
                           width: 120
                           height: 45
                           text: "Move Joint"
                           enabled: !refresh_switch_joint.checked && !button_freedrive.checked
                       }
                       Rectangle {
                           width: 150
                           height: 30
                           anchors.verticalCenter: row_joint_name.verticalCenter
                           id: rect_refresh_switch_joint
                           RefreshSwitch {
                               objectName: "refresh_switch_joint"
                               anchors.verticalCenter:rect_refresh_switch_joint.verticalCenter
                               anchors.horizontalCenter:rect_refresh_switch_joint.horizontalCenter
                               id: refresh_switch_joint
                           }
                       }
                       ComboBox {
                           id: comboBox_deecimals
                           objectName:"comboBox_deecimals"
                           Layout.alignment:Qt.AlignVCenter | Qt.AlignHCenter
                           width: 120
                           height: 40
                           font.pointSize: 10
                           font.family: "Arial"
                           wheelEnabled: true
                           displayText: "Decimals: " + currentText
                           model: [2, 1, 0]
                           indicator: Canvas {
                                    id: canvas
                                    x: comboBox_deecimals.width - width - comboBox_deecimals.rightPadding
                                    y: comboBox_deecimals.topPadding + (comboBox_deecimals.availableHeight - height) / 2
                                    width: 12
                                    height: 8
                                    contextType: "2d"
                                    onPaint: {
                                        context.reset();
                                        context.moveTo(0, 0);
                                        context.lineTo(width, 0);
                                        context.lineTo(width / 2, height);
                                        context.closePath();
                                        context.fill();
                                    }
                           }
                           background: Rectangle {
                                    implicitWidth: comboBox_deecimals.width
                                    implicitHeight: comboBox_deecimals.height
                                    border.color: comboBox_deecimals.pressed ? "#17a81a" : "Gray"
                                    border.width: 1
                                    radius: 5}
                       }

                    }
                    // Joint control slider // delegate {}里面一定不要加注释，否则design可能出现莫名的崩溃
                    Column {
                        anchors.horizontalCenter: column_joint_all.horizontalCenter
                        spacing: 5
                        Repeater {
                            objectName:"joint_repeater"
                            id: joint_control
                            //.push("first"); .pop(); strArray = []; strArray.length = 0
                            property var jointpose: joint_control.getjointpose()
                             model:[{"name": "Joint1/°", "objectName": "ctrlJoint1"},
                                 {"name": "Joint2/", "objectName": "ctrlJoint2"},
                                 {"name": "Joint3/°", "objectName":"ctrlJoint3"},
                                 {"name": "Joint4/°", "objectName": "ctrlJoint4"},
                                 {"name": "Joint5/°", "objectName": "ctrlJoint5"},
                                 {"name": "Joint6/°", "objectName": "ctrlJoint6"}]
                             delegate:SliderSpinBox{
                                 objectName:modelData.objectName
                                 name:modelData.name
                                 number:comboBox_deecimals.currentText
                                 stepSize: Math.pow(10, Math.abs(number-decimals))
                             }
                             function getjointpose(){
                                 var sum = [];
                                 for (var i = 0; i < joint_control.count; ++i) {
                                     sum.push(joint_control.itemAt(i).value)
                                 }
                                 return sum
                             }
//                             Component.onCompleted: {
//                                 for (var i = 0; i < joint_control.count; ++i) {
//                                     item.push(joint_control.itemAt(i))
//                                 }
//                              }
                        }
                    }
                    // Joint pose copy
                    Row{
                        anchors.horizontalCenter: column_joint_all.horizontalCenter
                        id: row_joint_pose
                        spacing: 5
                        Label {
                            anchors.verticalCenter: row_joint_pose.verticalCenter
                            id: label_joint_pose
                            width: 100
                            height: 30
                            color: "#000000"
                            text: qsTr("Joint Pose")
                            font.pointSize: swipeView.pointSize
                            font.family: "Times New Roman"
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                        }
                        TextField {
                            anchors.verticalCenter: row_joint_pose.verticalCenter
                            objectName:"text_joint_pose"
                            id: text_joint_pose
                            width: 385
                            height: 35
                            function gettextjoint(){
                                var sum = [];
                                for (var i = 0; i < joint_control.count; ++i) {
                                    sum.push(joint_control.itemAt(i).value)
                                }
                                return sum
//                                var sum = '';
//                                for (var i = 0; i < joint_control.count; ++i) {
//                                    if (i !== joint_control.count-1){ sum = sum + joint_control.itemAt(i).displayText +', '}
//                                    else {sum = sum + joint_control.itemAt(i).displayText}
//                                }
//                                return sum
                            }
                            text:text_joint_pose.gettextjoint().toString()
                            font.pointSize: swipeView.pointSize
                            font.family: "Times New Roman"
                            selectByMouse: true
                            horizontalAlignment: Text.AlignHCenter
                        }
                    }

                }

            }

            Rectangle {
                id: rect_tcp_all
                x: 439
                y: 453
                height: column_tcp_all.height+10
                width:  column_tcp_all.width+10
                border.color: "#bdbebf"
                border.width: 1
                radius: 15
                Column{
                    anchors.horizontalCenter: rect_tcp_all.horizontalCenter
                    anchors.verticalCenter: rect_tcp_all.verticalCenter
                    id: column_tcp_all
                    spacing: 10
                    // TCP name and refresh switch
                    Row {
                        anchors.horizontalCenter: column_tcp_all.horizontalCenter
                        id: row_tcp_name
                        x: 136
                        y: 432
                        spacing: 5
                        Label {
                           anchors.verticalCenter: row_tcp_name.verticalCenter
                           id: label_tcp_control
                           width: 100
                           height: 30
                           color: "#5d0909"
                           text: qsTr("TCP Control")
                           font.pointSize: swipeView.pointSize
                           font.family: "Arial"
                           horizontalAlignment: Text.AlignHCenter
                           verticalAlignment: Text.AlignVCenter
                       }
                       ColorButton {
                           anchors.verticalCenter: row_tcp_name.verticalCenter
                           objectName: "moveTCPButton"
                           id: button_move_tcp
                           width: 100
                           height: 45
                           text: "Move TCP"
                           enabled: !refresh_switch_tcp.checked && !button_freedrive.checked
                       }
                       Rectangle {
                           width: 150
                           height: 30
                           anchors.verticalCenter: row_tcp_name.verticalCenter
                           id: rect_RefreshSwitch
                           RefreshSwitch {
                               objectName: "refresh_switch_tcp"
                               anchors.verticalCenter:rect_RefreshSwitch.verticalCenter
                               anchors.horizontalCenter:rect_RefreshSwitch.horizontalCenter
                               id: refresh_switch_tcp
                           }
                       }
                       ComboBox {
                           id: comboBox_RvAndRpy
                           anchors.verticalCenter: row_tcp_name.verticalCenter
                           objectName:"comboBox_RvAndRpy"
                           width: 120
                           height: 40
                           font.pointSize: 10
                           font.family: "Arial"
                           wheelEnabled: true
                           currentIndex:0
                           model: ListModel {
                               id: rxItems
                               ListElement { text: "R vector/rad";    isdegree: false; name: "Rx/rad,Ry/rad,Rz/rad"}
                               ListElement { text: "R vector/degree"; isdegree: true;  name: "Rx/°,Ry/°,Rz/°"}
                               ListElement { text: "RPY/rad";         isdegree: false; name: "Roll/rad,Pitch/rad,Yaw/rad"}
                               ListElement { text: "RPY/degree";      isdegree: true;  name: "Roll/°,Pitch/°,Yaw/°"} }
                           property bool isdegree: rxItems.get(currentIndex).isdegree
                           property var name: rxItems.get(currentIndex).name.split(',')
                           textRole: 'text'
                           background: Rectangle {
                                    implicitWidth: comboBox_RvAndRpy.width
                                    implicitHeight: comboBox_RvAndRpy.height
                                    border.color: comboBox_deecimals.pressed ? "#17a81a" : "Gray"
                                    border.width: 1
                                    radius: 5}
                           indicator: Canvas {
                                    x: comboBox_deecimals.width - width - comboBox_deecimals.rightPadding
                                    y: comboBox_deecimals.topPadding + (comboBox_deecimals.availableHeight - height) / 2
                                    width: 12
                                    height: 8
                                    anchors.right: parent.right
                                    anchors.rightMargin: 5
                                    anchors.verticalCenterOffset: 0
                                    anchors.verticalCenter: parent.verticalCenter
                                    contextType: "2d"
                                    onPaint: {
                                        context.reset();
                                        context.moveTo(0, 0);
                                        context.lineTo(width, 0);
                                        context.lineTo(width / 2, height);
                                        context.closePath();
                                        context.fill();}    }     }

                    }
                    // TCP control slider
                    Grid{
                        anchors.horizontalCenter: column_tcp_all.horizontalCenter
                        rows : 3 //设置网格的行数，
                        columns: 2 //设置网格列数
                        //如果不进行行列数设置，会根据子项的多少自动设置，（行列数最相近原则）
                        flow: Grid.TopToBottom
                        spacing: 5
                        Repeater {
                             objectName: "tcp_repeater"
                             id: tcp_control
//                             property var item: []
                             model:[
                                 {"name": "X/mm", "from": -999, "to": 1020,"decimal":2,"objectName": "ctrlAxisX"},
                                 {"name": "Y/mm", "from": -999, "to": 1020,"decimal":2,"objectName": "ctrlAxisY"},
                                 {"name": "Z/mm", "from": -999, "to": 1020,"decimal":2,"objectName": "ctrlAxisZ"},
                                 {"name": comboBox_RvAndRpy.name[0], "from": comboBox_RvAndRpy.isdegree? -180: -3.2, "to": comboBox_RvAndRpy.isdegree? 180: 3.2,
                                     "decimal":comboBox_RvAndRpy.isdegree? 2: 4,"objectName": "ctrlRoll"},
                                 {"name": comboBox_RvAndRpy.name[1], "from": comboBox_RvAndRpy.isdegree? -180: -3.2, "to": comboBox_RvAndRpy.isdegree? 180: 3.2,
                                     "decimal":comboBox_RvAndRpy.isdegree? 2: 4,"objectName": "ctrlPitch"},
                                 {"name": comboBox_RvAndRpy.name[2], "from": comboBox_RvAndRpy.isdegree? -180: -3.2, "to": comboBox_RvAndRpy.isdegree? 180: 3.2,
                                     "decimal":comboBox_RvAndRpy.isdegree? 2: 4,"objectName": "ctrlYaw"},
                             ]
                             // delegate里面一定不要加注释，否则可能出现莫名的崩溃
                             delegate:Labelspinbox{
                                 name:modelData.name
                                 from:modelData.from
                                 to:modelData.to
                                 number:comboBox_deecimals.currentText
                                 decimals: modelData.decimal
                                 stepSize: Math.pow(10, Math.abs(number-decimals))
                             }

//                             Component.onCompleted: {
//                                 for (var i = 0; i < tcp_control.count; ++i) {
////                                     item.push(tcp_control.itemAt(i))
//                                     console.log(tcp_control.itemAt(i).stepSize)
////                                     console.log(item[i].value)
//                                 }
//                             }
                        }
                    }
                    //TCP pose copy
                    Row{
                        anchors.horizontalCenter: column_tcp_all.horizontalCenter
                        id: row_tcp_pose
                        spacing: 5
                        Label {
                            anchors.verticalCenter: row_tcp_pose.verticalCenter
                            id: label_tcp_pose
                            width: 100
                            height: 30
                            color: "#000000"
                            text: qsTr("TCP Pose")
                            font.pointSize: swipeView.pointSize
                            font.family: "Times New Roman"
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                        }
                        TextField {
                            anchors.verticalCenter: row_tcp_pose.verticalCenter
                            objectName:"text_tcp_pose"
                            id: text_tcp_pose
                            width: 385
                            height: 35
                            function gettexttcp(){
                                var sum = [];
                                for (var i = 0; i < tcp_control.count; ++i) {
                                    sum.push(tcp_control.itemAt(i).value)
                                }
                                return sum
//                                var sum = '';
//                                for (var i = 0; i < joint_control.count; ++i) {
//                                    if (i !== joint_control.count-1){ sum = sum + joint_control.itemAt(i).displayText +', '}
//                                    else {sum = sum + joint_control.itemAt(i).displayText}
//                                }
//                                return sum
                            }
                            text:text_tcp_pose.gettexttcp().toString()
                            font.pointSize: swipeView.pointSize
                            font.family: "Times New Roman"
                            selectByMouse: true
                            horizontalAlignment: Text.AlignHCenter
                        }

                    }

                }

            }

            Row{
                x: 432
                y: 16
                spacing:30
                ColorButton {
                    id: button_zero_position
                    objectName:"zeroButton"
                    width: 120
                    height: 45
                    text: "Zero Pose"
                }
                ColorButton {
                    id: button_stop
                    objectName:"stopButton"
                    width: 120
                    height: 45
                    text: "Stop Motion"
                }
                ColorButton {
                    id: button_freedrive
                    objectName:"freedriveButton"
                    width: 120
                    height: 45
                    checkable: true
                    text: button_freedrive.checked ? "Disabled": "(Pend)Enabled"
                    contentItem: Text {
                        text: button_freedrive.text
                        font:button_stop.font
                        verticalAlignment: Text.AlignVCenter
                        horizontalAlignment: Text.AlignHCenter
                        color: button_freedrive.checked ? "red" : "black"}
//                    }
                }
                ColorButton {
                    id: testbutton
                    objectName:"testbutton"
                    width: 80
                    height: 45
                    text: "TestPose"
                }
            }



            Column {
                id: column
                x: 973
                y: 108
                //                columnSpacing: 10
                spacing:10
                Label {
                    text: qsTr("Joint speed")
                    anchors.horizontalCenter: parent.horizontalCenter
                    font.pointSize: 16
                    font.family: "Arial"
                }
                SliderSpinBoxTwo {
                    id: sliderSpinBox_speedJ
                    objectName:"ctrlSpeedJ"
//                    property bool outflag: true
//                    Layout.alignment:Qt.AlignVCenter | Qt.AlignHCenter
//                    Layout.columnSpan: 2
//                    Layout.fillHeight: true
//                    Layout.fillWidth: true
                    width: 330
                    height: 40
                    name:"Joint speed"
                    from:0
                    decimals: 0
                    to:100
                    addtext: '%'
                    value:100
                }
                Label {
                    text: qsTr("TCP speed")
                    anchors.horizontalCenter: parent.horizontalCenter
                    font.pointSize: 16
                    font.family: "Arial"
                }
                SliderSpinBoxTwo {
                    id: sliderSpinBox_speedTCP
                    objectName:"ctrlSpeedTCP"
//                    property bool outflag: true
//                    Layout.alignment:Qt.AlignVCenter | Qt.AlignHCenter
//                    Layout.columnSpan: 2
                    width: 330
                    height: 40
                    name:"TCP speed"
                    from:0
                    to:100
                    decimals: 0
                    addtext: '%'
                    value:100
                }
                Label {
                    color: "#5d0909"
                    text: qsTr("Payload mass(kg) and 3Dcenter(m)")
                    anchors.horizontalCenter: parent.horizontalCenter
                    font.pointSize: 16
                    font.family: "Arial"
                }
                TextField {
                    id: payload_text
                    objectName: "payloadData"
                    width: 340
                    height: 50
                    text: "0, [0,0,0]"
                    font.pointSize: length ===0? 11 : 14
                    font.family: "Arial"
                    selectByMouse: true
                    placeholderText: qsTr("Division by Comma or space: 3, [0,0,0.3]")
                    placeholderTextColor: "#707070"
    //                onEditingFinished:{
                    //                    ip_textField.gettext(ip_textField.text)
                    //                }
                    Button {
                        id:save_payload
                        objectName: "savePayloadData"
                        text: qsTr("Save")
                        font.pointSize: 10
                        width: 50
                        height:parent.height
                        anchors.verticalCenter: parent.verticalCenter
                        anchors.right: parent.right
                        anchors.rightMargin: 0
                    }
                }


            }


//            GridLayout {
//                id: gridLayout1
//                x: 1012
//                y: 357
//                width: 320
//                height: 300
//                columnSpacing: 40
//                rowSpacing: 20
//                columns: 2
//                rows: 6

//            }
            Grid{
                x: 1009
                y: 377
                layoutDirection: Qt.RightToLeft
                rows: 6
                columns: 2
                columnSpacing: 30
                rowSpacing: 15
                ColorButton {objectName:'xaddButton';id: button1;width:120;height: 40;text:"X+" ; font.pointSize: 12;  }
                ColorButton {objectName:'xsubButton';id:button2;width:120;height: 40;text:"X-"; font.pointSize: 12; }
                ColorButton {objectName:'yaddButton';id: button3;width:120;height: 40;text:"Y+"; font.pointSize: 12; }
                ColorButton {objectName:'ysubButton';id: button4;width:120;height: 40;text:"Y-"; font.pointSize: 12;}
                ColorButton {objectName:'zaddButton';id: button5;width:120;height: 40;text:"Z+" ; font.pointSize: 12;}
                ColorButton {objectName:'zsubButton';id: button6; width:120;height: 40;text:"Z-" ; font.pointSize: 12;}

                ColorButton {objectName:'rxaddButton';id: button7; width:120;height: 40;text:"Roll+"; font.pointSize: 12; }
                ColorButton {objectName:'rxsubButton';id: button8; width:120;height: 40;text:"Roll-" ; font.pointSize: 12;}
                ColorButton {objectName:'ryaddButton';id: button9; width:120;height: 40;text:"Pitch+"; font.pointSize: 12;}
                ColorButton {objectName:'rysubButton';id: button10; width:120;height: 40;text:"Pitch-" ; font.pointSize: 12;}
                ColorButton {objectName:'rzaddButton';id: button11; width:120;height: 40;text:"Yaw+" ; font.pointSize: 12;}
                ColorButton {objectName:'rzsubButton';id: button12; width:120;height: 40;text:"Yaw-"; font.pointSize: 12; }
            }




            GridLayout {
                id: gridLayout2
                x: 28
                y: 404
                columnSpacing: 30
                rowSpacing: 15
//                space: 10
                columns: 3
                rows: 4
                RoundButton {
                    id: button_unlock
                    Layout.columnSpan: 3
                    width: 190
                    height: 45
                    objectName: "unlockButton"
                    text: "Unlock protective stop"
                    Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter
                    enabled: comboBox_safe_mode.displayText === "PROTECTIVE_STOP" ? true : false
                    background: Rectangle {
                        color: button_unlock.down ? "lightGray" : "#9999FF"
                        radius: 10
                        border.color: "#bdbebf"
                        implicitWidth: button_unlock.width
                        implicitHeight: button_unlock.height
                        border.width: 2
                    }
                    font.pointSize: swipeView.pointSize
                    font.family: "Arial"
                    contentItem: Text {
                        text: button_unlock.text
                        verticalAlignment: Text.AlignVCenter
                        horizontalAlignment: Text.AlignHCenter
                        font: button_unlock.font
                        color: comboBox_safe_mode.displayText === "PROTECTIVE_STOP" ? "red" : "gray"}
                    onEnabledChanged: {
                        if (enabled === true){
                            rB_poweron.enabled = false
                        }
                        if (enabled === false){
                            rB_poweron.enabled = true
                        }
                    }
                }

                RoundButton {id: rB_poweron;objectName: "rB_poweron"; width: 90; height: 45; text: "Power on"; font.pointSize: 12; font.family: "Arial";
                    background: Rectangle { color: rB_poweron.down ? "lightGray" : "#9999FF"; radius: 10; border.color: "#bdbebf"; border.width: 2;
                        implicitHeight: 45; implicitWidth: 90}
                    onClicked: { rB_poweron.enabled = false;
                        rB_poweroff.enabled = true;
//                        rB_release.enabled = true;
                    }
                }
                RoundButton {id: rB_release;objectName: "rB_release"; width: 90; height: 45; text: "Brake release"; font.pointSize: 12; font.family: "Arial";enabled:false;
                    background: Rectangle { color: rB_release.down ? "lightGray" : "#9999FF"; radius: 10; border.color: "#bdbebf"; border.width: 2;
                        implicitHeight: 45; implicitWidth: 90}
                    onClicked: {
                        rB_release.enabled = false; }
                }
                RoundButton {id: rB_poweroff;objectName: "rB_poweroff"; width: 90; height: 45; text: "Power off"; font.pointSize: 12; font.family: "Arial";enabled: false;
                    background: Rectangle { color: rB_poweroff.down ? "lightGray" : "#9999FF"; radius: 10; border.color: "#bdbebf"; border.width: 2;
                        implicitHeight: 45; implicitWidth: 90}
                    onClicked: { //rB_poweron.checked = false;
                        rB_release.enabled = false;
                        rB_poweroff.enabled = false;
                        rB_poweron.enabled = true;}
                }
                Row{
                    Layout.alignment:Qt.AlignVCenter | Qt.AlignHCenter
                    Layout.columnSpan: 3
                    spacing: 35
                    RoundButton {id: rB_restart_safety;objectName: "rB_restart_safety"; width: 150; height: 45; text: "Restart safety"; font.pointSize: 12; font.family: "Arial";
                        background: Rectangle { color: rB_restart_safety.down ? "lightGray" : "#9999FF"; radius: 10; border.color: "#bdbebf"; border.width: 2;
                            implicitHeight: 45; implicitWidth: 150}
                        onClicked: { //rB_poweron.checked = false;
                            rB_release.enabled = false;
                            rB_poweroff.enabled = false;
                            rB_poweron.enabled = true;}
                    }
                    RoundButton {id: rB_shutdown; objectName: "rB_shutdown";width: 150; height: 45; text: "Shutdown"; font.pointSize: 12; font.family: "Arial";
                        background: Rectangle { color: rB_shutdown.down ? "lightGray" : "#9999FF"; radius: 10; border.color: "#bdbebf"; border.width: 2;
                            implicitHeight: 45; implicitWidth: 150} }
                }


                Row {
                    id: row_robot_mode
                    Layout.alignment:Qt.AlignVCenter | Qt.AlignHCenter
                    Layout.columnSpan: 3
                    spacing: 5
                    Label {
                        anchors.verticalCenter: row_robot_mode.verticalCenter
                        id: label_robot_mode
                        width: 100
                        height: 30
                        color: "#000000"
                        text: qsTr("Robot mode")
                        font.pointSize: swipeView.pointSize
                        font.family: "Times New Roman"
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }
                    ComboBox {
                        id: comboBox_robot_mode
                        objectName: "comboBox_robotM"
                        Layout.alignment:Qt.AlignVCenter | Qt.AlignHCenter
                        width: 250
                        height: 40
                        font.pointSize: 10
                        font.family: "Arial"
                        wheelEnabled: true
                        textRole: "text"
//                        displayText: currentText
                        model:ListModel {
                            id: robot_modeItems
                            ListElement { text: "NO_CONTROLLER";    color: "Black"; }
                            ListElement { text: "DISCONNECTED";     color: "Black"; }
                            ListElement { text: "CONFIRM_SAFETY";   color: "Black"; }
                            ListElement { text: "BOOTING";          color: "Black"; }
                            ListElement { text: "POWER_OFF";        color: "Black"; }
                            ListElement { text: "POWER_ON";         color: "Black"; }
                            ListElement { text: "IDLE";             color: "Black"; }
                            ListElement { text: "BACKDRIVE";        color: "Black"; }
                            ListElement { text: "RUNNING";          color: "Black"; }
                            ListElement { text: "UPDATING_FIRMWARE";color: "Black"; }}

//                        model: ['NO_CONTROLLER',
//                            'DISCONNECTED',
//                            'CONFIRM_SAFETY',
//                            'BOOTING',
//                            'POWER_OFF',
//                            'POWER_ON',
//                            'IDLE',
//                            'BACKDRIVE',
//                            'RUNNING',
//                            'UPDATING_FIRMWARE']
                        // value from -1 to 8
                        indicator: Canvas {
                                 width: 12
                                 height: 8
                                 anchors.right: parent.right
                                 anchors.verticalCenter: parent.verticalCenter
                                 anchors.rightMargin: 5
                                 contextType: "2d"
                                 onPaint: {
                                     context.reset();
                                     context.moveTo(0, 0);
                                     context.lineTo(width, 0);
                                     context.lineTo(width / 2, height);
                                     context.closePath();
                                     context.fill();
                                 }
                        }
                        background: Rectangle {
                                 implicitWidth: comboBox_robot_mode.width
                                 implicitHeight: comboBox_robot_mode.height
                                 border.color: comboBox_deecimals.pressed ? "#17a81a" : "Gray"
                                 border.width: 1
                                 radius: 5}
                        onDisplayTextChanged: {
                            if (displayText == "POWER_OFF"){
                                rB_poweroff.enabled = false; rB_poweron.enabled = true}
                            if (displayText == "POWER_ON" || displayText == "RUNNING"){
                                rB_poweroff.enabled = true;  rB_poweron.enabled = false}
                            if (displayText == "IDLE"){
                             rB_release.enabled = true;}
                        }
                    }

                }

                Row {
                    id: row_safe_mode
                    Layout.alignment:Qt.AlignVCenter | Qt.AlignHCenter
                    Layout.columnSpan: 3
                    spacing: 5
                    Label {
                        anchors.verticalCenter: row_safe_mode.verticalCenter
                        id: label_safe_mode
                        width: 100
                        height: 30
                        color: "#000000"
                        text: qsTr("Safety mode")
                        font.pointSize: swipeView.pointSize
                        font.family: "Times New Roman"
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }
                    ComboBox {
                        id: comboBox_safe_mode
                        Layout.alignment:Qt.AlignVCenter | Qt.AlignHCenter
                        width: 250
                        height: 40
                        font.pointSize: 10
                        font.family: "Arial"
                        wheelEnabled: true
//                        displayText: currentText
                        textRole: "text"
                        model:ListModel {
                            id: safe_modeItems
                            ListElement { text: "NORMAL";               color: "Black"; }
                            ListElement { text: "REDUCED";              color: "Black"; }
                            ListElement { text: "PROTECTIVE_STOP";      color: "Red"; }
                            ListElement { text: "SAFEGUARD_STOP";       color: "Red"; }
                            ListElement { text: "SYSTEM_EMERGENCY_STOP";color: "Red"; }
                            ListElement { text: "ROBOT_EMERGENCY_STOP"; color: "Red"; }
                            ListElement { text: "VIOLATION";            color: "Red"; }
                            ListElement { text: "FAULT";                color: "Red"; }
                            ListElement { text: "VALIDATE_JOINT_ID";    color: "Black"; }
                            ListElement { text: "UNDEFINED_SAFETY_MODE";color: "Red"; }}
//                        model: ['NORMAL',
//                                 'REDUCED',
//                                 'PROTECTIVE_STOP',
//                                 'RECOVERY',
//                                 'SAFEGUARD_STOP',
//                                 'SYSTEM_EMERGENCY_STOP',
//                                 'ROBOT_EMERGENCY_STOP',
//                                 'VIOLATION',
//                                 'FAULT',
//                                 'VALIDATE_JOINT_ID',
//                                 'UNDEFINED_SAFETY_MODE']
                        contentItem: Text {
                                 leftPadding: 10
                                 rightPadding: comboBox_safe_mode.indicator.width + comboBox_safe_mode.spacing
                                 text: comboBox_safe_mode.displayText
                                 font: comboBox_safe_mode.font
                                 color: safe_modeItems.get(comboBox_safe_mode.currentIndex).color
                                 verticalAlignment: Text.AlignVCenter
                                 elide: Text.ElideRight
                             }
                        // value from 1 to 11
                        indicator: Canvas {
                                 width: 12
                                 height: 8
                                 anchors.verticalCenter: parent.verticalCenter
                                 anchors.right: parent.right
                                 anchors.rightMargin: 5
                                 contextType: "2d"
                                 onPaint: {
                                     context.reset();
                                     context.moveTo(0, 0);
                                     context.lineTo(width, 0);
                                     context.lineTo(width / 2, height);
                                     context.closePath();
                                     context.fill();
                                 }
                        }
                        background: Rectangle {
                                 implicitWidth: comboBox_safe_mode.width
                                 implicitHeight: comboBox_safe_mode.height
                                 border.color: comboBox_deecimals.pressed ? "#17a81a" : "Gray"
                                 border.width: 1
                                 radius: 5}
//                        onActivated: {console.log(currentIndex,currentText) }
                    }

                }
            }

            RoundButton {
                id: rB_emergency_stop
                objectName: "emergencyStopButton"
                x: 1049
                y: 22
                width: 190
                height: 80
                text: rB_emergency_stop.checked ? "Click to release": "(Pend)Emergency stop"
                font.pointSize: 18
                font.family: "Arial"
                checkable: true
                background: Rectangle {
                    color: rB_emergency_stop.checked ? "lightGray" : "red"; radius: 20; border.color: "#bdbebf"; border.width: 2;
                    implicitHeight: 80; implicitWidth: 190}
            }








        }
      }

//    PySignal {
//        id: pysignal
//        jointSpeed: sliderSpinBox_speedJ.value
//        tcpSpeed: sliderSpinBox_speedTCP.value
//        jointPose: text_joint_pose.gettextjoint()
//        tcpPose: text_tcp_pose.gettexttcp()
////        tcpSwitch: refresh_switch_tcp.checked
//        //槽
//        function jointSChange(jvalue) {sliderSpinBox_speedJ.value = jvalue}
//        function tcpSChange(tvalue) {sliderSpinBox_speedTCP.value = tvalue}
//        function jointPChange(jvalue){
////            console.log('jointPChange',jvalue)
//            for (var i = 0; i < joint_control.count; ++i) {
//                joint_control.itemAt(i).value = jvalue[i]
//            }
//        }
//        function tcpPChange(tvalue) {
////            console.log('setTCPvalue',tvalue)
//            for (var i = 0; i < tcp_control.count; ++i) {
//                tcp_control.itemAt(i).value = tvalue[i]
//            }
//        }
////        function getSwitchT(){
////            console.log('getSwitchT',refresh_switch_tcp.checked)
////            get_tcp_switch_slot(refresh_switch_tcp.checked)
////        }
//        signal tcpSwiChecked()
//        // 信号 连接 QML 槽
//        Component.onCompleted: {
//            jointSpeedChanged.connect(jointSChange)
//            tcpSpeedChanged.connect(tcpSChange)
//            jointPoseChanged.connect(jointPChange)
//            tcpPoseChanged.connect(tcpPChange)
//            PySignal.tcpSwitchChecked.connect(tcpSwiChecked)
//        }
//    }
//    Connections {
//        target: pysignal
//        function onTcpSwiChecked(){console.log('onTcpSwitchChecked');
//            PySignal.get_tcp_switch_slot(refresh_switch_tcp.checked)}
//    }



    // 构造Binding对象需要花一点时间，这个对于特别大的程序可能会有一定影响。
    Binding {target: urSingal; property: "tcpSpeed";value: sliderSpinBox_speedTCP.value;} //velocity unit: percent when: sliderSpinBox_speedJ.flag
    Binding {target: urSingal;  property: "jointSpeed";  value: sliderSpinBox_speedJ.value;}
    Binding {target: urSingal;  property: "tcpPose";  value: text_tcp_pose.gettexttcp();}
    Binding {target: urSingal;  property: "jointPose";  value: text_joint_pose.gettextjoint()}
    Binding {target: urSingal;  property: "tcpSwitch";  value: refresh_switch_tcp.checked}
    Binding {target: urSingal;  property: "jointSwitch";  value: refresh_switch_joint.checked}
    Binding {target: urSingal;  property: "rvRpyIndex";  value: comboBox_RvAndRpy.currentIndex}
    Connections {
        target: urSingal
        function onJointSpeedRevised(jvalue) {
//            console.log('onJointSpeedChanged',jvalue)
            sliderSpinBox_speedJ.value = jvalue
        }
        function onTcpSpeedRevised(tvalue) {
//            console.log('onTcpSpeedChanged',tvalue)
            sliderSpinBox_speedTCP.value = tvalue
        }
        function onJointPoseRevised(jvalue){
//            console.log('jointPChange',jvalue)
            for (var i = 0; i < joint_control.count; ++i) {
                joint_control.itemAt(i).value = jvalue[i]
            }
        }
        function onTcpPoseRevised(tvalue) {
//            console.log('setTCPvalue',tvalue)
            for (var i = 0; i < tcp_control.count; ++i) {
//                console.log(tvalue[i])
                tcp_control.itemAt(i).value = tvalue[i]
            }
        }
        function onTcpSwitchChecked(value) {
//            console.log('onTcpSwitchChecked',value)
            refresh_switch_tcp.checked = value
        }
        function onJointSwitchChecked(value) {
//            console.log('onJointSwitchChecked',value)
            refresh_switch_joint.checked = value
        }
        function onRvRpyIndexActivated(index) {
//            console.log('onRvRpyIndexActivated',value)
            comboBox_RvAndRpy.currentIndex = index
        }
        function onSetSafeMode(index) {
            comboBox_safe_mode.currentIndex = index-1
        }
        function onSetRobotMode(index) {
            comboBox_robot_mode.currentIndex = index+1
        }
    }


//        function onGetJvalue(){
//            var sum = [];
//            for (var i = 0; i < joint_control.count; ++i) {
//                sum.push(joint_control.itemAt(i).value)
//            }
//            pySingal.getJvalue_slot(sum)
//        }
//        function onSetJvalue(jvalue) {
//            console.log('onSetJvalue',jvalue)
//            for (var i = 0; i < joint_control.count; ++i) {
//                joint_control.itemAt(i).value = jvalue[i]
//            }

}


        //        currentIndex: 1

        //    PageIndicator {
        //         id: indicator
        //         count: swipeView.count
        //         currentIndex: swipeView.currentIndex
        //         anchors.bottom: swipeView.bottom
        //         anchors.horizontalCenter: parent.horizontalCenter
        //     }










/*##^##
Designer {
    D{i:0;formeditorZoom:0.6600000262260437}D{i:2;invisible:true}D{i:7;anchors_x:8;anchors_y:432}
D{i:12;anchors_x:8;anchors_y:432}D{i:15;anchors_x:8;anchors_y:432}D{i:14;anchors_x:8;anchors_y:432}
D{i:17;anchors_x:8;anchors_y:432}D{i:18;anchors_x:8;anchors_y:432}D{i:16;anchors_x:8;anchors_y:432}
D{i:11;anchors_x:8;anchors_y:432}D{i:21;anchors_x:8;anchors_y:432}D{i:20;anchors_x:8;anchors_y:432}
D{i:19;anchors_x:8;anchors_y:432}D{i:23;anchors_x:8;anchors_y:432}D{i:24;anchors_x:8;anchors_y:432}
D{i:22;anchors_x:8;anchors_y:432}D{i:10;anchors_x:8;anchors_y:432}D{i:9;anchors_x:8;anchors_y:432}
D{i:28;anchors_x:8;anchors_y:432}D{i:29;anchors_x:8;anchors_y:432}D{i:31;anchors_x:8;anchors_y:432}
D{i:30;anchors_x:8;anchors_y:432}D{i:33;anchors_x:8;anchors_y:432}D{i:34;anchors_x:8;anchors_y:432}
D{i:35;anchors_x:8;anchors_y:432}D{i:32;anchors_x:8;anchors_y:432}D{i:27;anchors_x:8;anchors_y:432}
D{i:26;anchors_x:8;anchors_y:432}D{i:25;anchors_x:8;anchors_y:432}
}
##^##*/
