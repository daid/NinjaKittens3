import QtQuick 2.1
import QtQuick.Controls 1.0
import QtQuick.Layouts 1.1

RowLayout {
    implicitHeight: 30
    implicitWidth: parent.width

    Text {
        Layout.preferredWidth: 100
        horizontalAlignment: Text.AlignLeft
        verticalAlignment: Text.AlignVCenter
        text: item.type.label
    }

    TextField {
        Layout.fillWidth: true
        horizontalAlignment: Text.AlignLeft
        verticalAlignment: Text.AlignVCenter
        text: item.value
        placeholderText: item.type.default_value
        validator: DoubleValidator{}
        Keys.onReleased: {
            item.value = text
        }
        onEditingFinished: {
            item.value = text
        }

        Text {
            anchors.right: parent.right
            anchors.rightMargin: 5
            anchors.verticalCenter: parent.verticalCenter

            color: '#808080'
            text: item.type.unit
        }
    }
}
