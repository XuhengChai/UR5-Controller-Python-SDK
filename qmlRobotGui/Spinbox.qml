import QtQuick 2.13
import QtQuick.Window 2.13
import QtQuick.Controls 2.3


SpinBox {
    id: spinbox
    property int decimals: 2
    property real factor: Math.pow(10, decimals)
    property real realValue: value / factor
    property string addtext: ''

//    value: 0
    stepSize: 1
    wheelEnabled: true
    editable: true
    font.pointSize: 12
    font.family: "Arial"
//    inputMethodHints:Qt.ImhHiddenText


    validator: DoubleValidator {
                bottom: Math.min(spinbox.from, spinbox.to)*spinbox.factor
                decimals: spinbox.decimals
                top:  Math.max(spinbox.from, spinbox.to)*spinbox.factor
    }

    textFromValue: function(value, locale) {
        return Number(value / spinbox.factor).toLocaleString(locale, 'f', spinbox.decimals)
    }
    
    valueFromText: function(text, locale) {
//        console.log(text,Math.round(Number.fromLocaleString(locale, text)*spinbox.factor))

        return Math.round(Number.fromLocaleString(locale, text) * spinbox.factor)
    }

    contentItem: TextInput {
        id: textInput
        z: 2
        text: spinbox.displayText
        //        text: spinbox.textFromValue(spinbox.value,spinbox.locale)
        selectByMouse: true

        font: spinbox.font
        color: spinbox.palette.text
        selectionColor: spinbox.palette.highlight
        selectedTextColor: spinbox.palette.highlightedText
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Qt.AlignVCenter
        readOnly: !spinbox.editable
        validator: spinbox.validator
        inputMethodHints: spinbox.inputMethodHints
        Text {
            text: spinbox.addtext
            font.pointSize: 12
            font.family: "Arial"
            anchors.verticalCenter: rectangle.verticalCenter
            anchors.right: rectangle.right
            anchors.rightMargin: 2
            horizontalAlignment: Qt.AlignRight
        }

        Rectangle {
            id: rectangle
            x: -6 - (spinbox.down.indicator ? 1 : 0)
            y: -6
            width: spinbox.width - (spinbox.up.indicator ? spinbox.up.indicator.width - 1 : 0) - (spinbox.down.indicator ? spinbox.down.indicator.width - 1 : 0)
            height: spinbox.height
            visible: spinbox.activeFocus
            color: "transparent"
            border.color: spinbox.palette.highlight
            border.width: 2

        }

    }
    up.indicator: Rectangle {
             x: spinbox.mirrored ? 0 : parent.width - width
             implicitWidth: 40
             implicitHeight: 40
             border.color: "#bdbebf"
             border.width: 2
             radius: 2
             color: spinbox.up.pressed ? "#bdbebf" : "#ffffff"
//             gradient: Gradient {
//                      GradientStop { position: 0.0; color: spinbox.up.pressed ? "#f6f6f6" : "lightsteelblue" }
//                      GradientStop { position: 1.0; color: spinbox.up.pressed ? "#f6f6f6" : "#9999FF" }   }
             Text {
                 text: "+"
                 font.pixelSize: spinbox.font.pixelSize * 2
                 anchors.fill: parent
                 fontSizeMode: Text.Fit
                 horizontalAlignment: Text.AlignHCenter
                 verticalAlignment: Text.AlignVCenter
             }
         }
    down.indicator: Rectangle {
             x: spinbox.mirrored ? parent.width - width : 0
             implicitWidth: 40
             implicitHeight: 40
             border.color: "#bdbebf"
             border.width: 2
             radius: 2
             color: spinbox.down.pressed ? "#bdbebf" : "#ffffff"
//             gradient: Gradient {
//                      GradientStop { position: 0.0; color: spinbox.down.pressed ? "#f6f6f6" : "lightsteelblue" }
//                      GradientStop { position: 1.0; color: spinbox.down.pressed ? "#f6f6f6" : "#9999FF" }   }
             Text {
                 text: "-"
                 font.pixelSize: spinbox.font.pixelSize * 2
                 anchors.fill: parent
                 fontSizeMode: Text.Fit
                 horizontalAlignment: Text.AlignHCenter
                 verticalAlignment: Text.AlignVCenter
             }
         }

}

/*##^##
Designer {
    D{i:0;formeditorZoom:1.5}
}
##^##*/
