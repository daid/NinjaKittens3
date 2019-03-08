import QtQuick 2.1
import QtQuick.Controls 1.0
import QtQuick.Layouts 1.1

RowLayout {
    implicitHeight: 30
    implicitWidth: parent.width

    Text {
        Layout.alignment: Qt.AlignTop
        Layout.fillWidth: true
        Layout.preferredHeight: 30
        horizontalAlignment: Text.AlignLeft
        verticalAlignment: Text.AlignVCenter
        text: setting.type.label
    }

    Loader
    {
        Layout.preferredWidth: 75
        source: "settings/" + setting.type.type + ".qml"
    }
}
