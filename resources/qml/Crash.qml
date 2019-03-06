import QtQuick 2.2
import QtQuick.Controls 1.0
import QtQuick.Layouts 1.0
import QtQuick.Dialogs 1.0
import QtQuick.Window 2.0


Window {
    visible: true
    modality: "ApplicationModal"
    flags: "Dialog"

    title: qsTr("Oops...")
    width: 640
    height: 640

    ColumnLayout {
        anchors.fill: parent

        Text {
            text: "Oops, we encountered an issue. We hope the following kitten makes it a bit better:"
        }
        Image {
            source: "http://www.randomkittengenerator.com/cats/rotator.php"
            onStatusChanged: if (status == Image.Error) source = "../images/kitten.jpg"
        }
        Text {
            text: "Details:"
        }
        TextArea {
            Layout.fillHeight: true
            Layout.fillWidth: true
            text: crash_info
            readOnly: true
        }
    }
}
