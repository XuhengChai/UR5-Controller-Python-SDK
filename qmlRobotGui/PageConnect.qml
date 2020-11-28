import QtQuick 2.13
import QtQuick.Window 2.13
import QtQuick.Controls 2.3

Rectangle {
    id: page1
    width: 960
    height: 720
    color: "#efeeee"
    visible: true
    opacity: visible
    Row {
        anchors.horizontalCenter: page1.horizontalCenter
        anchors.verticalCenter: page1.verticalCenter
        visible: page1.visible
//                opacity: 0
        spacing: 10
            TextField {
                id: ip_textField
//                signal gettext(string text)
                objectName: "ipAddress"
                width: 500
                height: 50
                text: "192.168.1.102"
                font.pointSize: 14
                font.family: "Arial"
                selectByMouse: true
                placeholderText: qsTr("Please input the IP adreess")
                placeholderTextColor: "#707070"
//                onEditingFinished:{
//                    ip_textField.gettext(ip_textField.text)
//                }
            }

            Button {
                id: connect_button
                objectName: "connectButton"
                width: 150
                height: ip_textField.height
                text: connect_button.checked? qsTr("Cancelling...") : 'Connect'
                checkable: true
                font.pointSize: 14
                font.family: "Arial"
//                property bool onoff: true
//                onClicked: {
//                    if (connect_button.onoff){
//                        connect_button.text = "Cancelling...";
////                        swipeView.setCurrentIndex(swipeView.currentIndex+1)
////                        var index = swipeView.currentIndex
////                        swipeView.currentIndex = index+1
//                        connect_button.onoff = false
//                    }
//                    else {
//                        connect_button.text = "Connect";
//                        connect_button.onoff = true
//                    }
//                }
            }
    }

    Label {
        id: label1
        x: 45
        y: 80
        text: qsTr("Universal Robot")
        font.pointSize: 26
        color: "#c110ea"
        font.bold: true
        font.family: "Arial"
        width: 300
        height: 60
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
    }


}

