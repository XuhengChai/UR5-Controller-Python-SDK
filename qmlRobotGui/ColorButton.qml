import QtQuick 2.13
import QtQuick.Window 2.13
import QtQuick.Controls 2.3

RoundButton {
    id: colorButton
    font.family: "Arial"
    width: 120
    height: 30
    background: Rectangle {
        radius: 10
        gradient: Gradient {
            GradientStop { position: 0; color: colorButton.down ? "lightGray" : "#ffffff";}
            GradientStop { position: 1; color: colorButton.down ? "lightGray" :"#ccccff";}
        }
        implicitHeight: colorButton.height
        border.width: 2
        implicitWidth: colorButton.width
        border.color: "#bdbebf"
    }
    font.pointSize: swipeView.pointSize
}
