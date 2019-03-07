import QtQuick 2.1
import QtQuick.Controls 1.0
import QtQuick.Layouts 1.1

TextField {
    property string unit: ""

    horizontalAlignment: Text.AlignLeft
    verticalAlignment: Text.AlignVCenter
    text: setting.value
    placeholderText: setting.type.default_value
    validator: RegExpValidator { regExp: /[0-9]*\.?[0-9]*/ }
    Keys.onReleased: {
        setting.value = text
    }
    onEditingFinished: {
        setting.value = text
    }

    Text {
        anchors.right: parent.right
        anchors.rightMargin: 5
        anchors.verticalCenter: parent.verticalCenter

        color: '#808080'
        text: unit
    }
}
