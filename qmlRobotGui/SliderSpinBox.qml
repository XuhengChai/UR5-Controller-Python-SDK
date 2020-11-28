import QtQuick 2.13
import QtQuick.Window 2.13
import QtQuick.Controls 2.3

Item {
    objectName: 'sliderspinbox'
    id: sliderbox
    height: 40
    width: 500
    property string name: 'Joint1/°'
    property real value: 0.0
//    property real getvalue: spinbox.realValue
    property real radius: 10.0
    property real from: -180
    property real to: 180
    property int number: 0
    property alias displayText: spinbox.displayText
    property alias decimals: spinbox.decimals
    property alias addtext: spinbox.addtext
    property alias stepSize:spinbox.stepSize
//    property bool innerflag: true
//    property bool outflag: true
//    onValueChanged: {
//        if (slider.value !== Math.round(sliderbox.value*spinbox.factor)){
//            slider.value = Math.round(sliderbox.value*spinbox.factor)
//        }
//    }

//    property var propotion: ['1',4/8,3/8]
//    function SetPropotion(){
//        var sum = 0
//        for (var i = 0; i < propotion.length; ++i) {
//            sum+= Number.fromLocaleString(propotion.toLocaleString())
//        }
//        return propotion.pop(0)

//    }

    Rectangle {
        id: parent_rectangle
        width: sliderbox.width
        height: sliderbox.height
        color: "#FFFFFF"
        radius: sliderbox.radius
        Row {
            id: row
            width: sliderbox.width
            height: sliderbox.height
            anchors.horizontalCenter: parent_rectangle.horizontalCenter
            anchors.verticalCenter: parent_rectangle.verticalCenter
            spacing: 5
            Rectangle { id: rectangle;
                width: (sliderbox.width-row.spacing*2)*5/32;
                height: sliderbox.height; radius: sliderbox.radius;
                anchors.verticalCenter: parent.verticalCenter;
//                color: "#ded3f0"
//                gradient: Gradient {
//                         GradientStop { position: 0.0; color: "lightsteelblue" }
//                         GradientStop { position: 1.0; color: "#9999FF" }   }

                Text {
                    width: rectangle.width
                    height: rectangle.height
                    text: sliderbox.name
                    font.pointSize: 12
                    verticalAlignment: Text.AlignVCenter
                    horizontalAlignment: Text.AlignHCenter
                    font.family: "Arial"
                    anchors.verticalCenter: rectangle.verticalCenter
                }
            }

            Slider {
                id: slider
                width: (sliderbox.width-row.spacing*2)*16/32
                height: sliderbox.height
                stepSize: 1
                wheelEnabled: true
                to: sliderbox.to*spinbox.factor
                from: sliderbox.from*spinbox.factor
                value: Math.round(sliderbox.value*spinbox.factor)
                onValueChanged: {
//                    console.log(slider.value)
//                    sliderbox.innerflag = false
                    if (spinbox.value !== slider.value){
                        spinbox.value = slider.value
                    }
                }

            }

            Spinbox {
                id: spinbox
                from: sliderbox.from * spinbox.factor
                to: sliderbox.to * spinbox.factor
                value: Math.round(sliderbox.value*spinbox.factor)
                width: (sliderbox.width-row.spacing*2)*11/32
                height: sliderbox.height
                font.pointSize: 12
                onValueModified: {
//                    sliderbox.innerflag = true
                    if (slider.value !== spinbox.value){
                        slider.value = spinbox.value
                    }
//                    slider.value = slider.value.toFixed(spinbox.decimals)
//                    console.log(slider.value*spinbox.factor)
                }
//                Binding {target: slider;  property: "value";  value: (spinbox.value/spinbox.factor);when: sliderbox.innerflag} // 同注释onValueModified
                Binding {target: sliderbox;  property: "value";  value: spinbox.value/spinbox.factor}

            }
        }

    }
//    onNumberChanged:{
//        console.log(number,sliderbox.decimals)
//        spinbox.stepSize = Math.pow(10, Math.abs(number-sliderbox.decimals))
//    }

}
