import QtQuick 2.1
import QtQuick.Controls 1.0
import QtQuick.Layouts 1.1

RowLayout {
    implicitHeight: 30
    implicitWidth: parent.width

    Text {
        Layout.fillWidth: true
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
