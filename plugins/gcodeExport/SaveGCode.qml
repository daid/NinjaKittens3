import QtQuick 2.2
import QtQuick.Controls 1.0
import QtQuick.Layouts 1.0
import QtQuick.Dialogs 1.0
import NK3 1.0 as NK3


Item {
    implicitHeight: childrenRect.height

    Button {
        anchors.top: parent.top
        anchors.right: parent.right

        text: "Save"

        onClicked: export_file_dialog.visible = true
    }

    FileDialog {
        id: export_file_dialog
        title: "Please choose a file"
        nameFilters: ["GCode files (*.gcode *.nc *.g)"]
        selectExisting: false

        onAccepted: {
            output_method.save(fileUrls[0]);
        }
    }
}
