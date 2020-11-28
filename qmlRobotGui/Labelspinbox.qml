import QtQuick 2.13
import QtQuick.Window 2.13
import QtQuick.Controls 2.3

Item {
    objectName: 'lablespinbox'
    id: labelbox
    height: 40
    width: 250
    property string name: 'X/mm'
    property real value: 0.0
    property real from: 0.0
    property real to: 0.0
    property real radius: 5.0
    property int number: 0
    property alias displayText: spinbox.displayText
    property alias decimals: spinbox.decimals
    property alias stepSize:spinbox.stepSize
    Row {
        id: row
        width: labelbox.width
        height: labelbox.height
        anchors.horizontalCenter: labelbox.horizontalCenter
        anchors.verticalCenter: labelbox.verticalCenter
        spacing: 5

         Rectangle { id: rectangle

             height: labelbox.height;
             radius: labelbox.radius;
             width: (labelbox.width-row.spacing)*5/16
             Text {
                 width: rectangle.width
                 height: rectangle.height
                 text: labelbox.name
                 anchors.horizontalCenter: parent.horizontalCenter
                 font.pointSize: 12
                 verticalAlignment: Text.AlignVCenter
                 horizontalAlignment: Text.AlignHCenter
                 font.family: "Arial"
                 anchors.verticalCenter: parent.verticalCenter
             }


         }
         Spinbox {
             id: spinbox
             from: labelbox.from*spinbox.factor
             to: labelbox.to*spinbox.factor
             width: (labelbox.width-row.spacing)*11/16
             height: labelbox.height
             value: Math.round(labelbox.value*spinbox.factor)
             font.pointSize: 12
//             onValueChanged:{labelbox.value = spinbox.value/spinbox.factor}
             Binding {target: labelbox;  property: "value";  value: spinbox.value/spinbox.factor} // 同注释onValueModified


         }
     }
//    onNumberChanged:{
//        spinbox.stepSize = Math.pow(10, Math.abs(number-2))

//    }
}
