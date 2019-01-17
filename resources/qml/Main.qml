import QtQuick 2.2
import QtQuick.Controls 1.0
import QtQuick.Layouts 1.0
import QtQuick.Dialogs 1.0
import NK3 1.0 as NK3

NK3.MainWindow {
    visible: true
    width: 640
    height: 480
    title: qsTr("NinjaKittens 3")

    NK3.MouseHandler {
        anchors.fill: parent
    }

    ToolBar {
        id: toolbar
        height: 28
        Row {
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            ToolButton {
                anchors.top: parent.top
                anchors.bottom: parent.bottom
                text: "Quit"
                onClicked: {
                    Qt.quit()
                }
            }
            ToolButton {
                anchors.top: parent.top
                anchors.bottom: parent.bottom
                text: "Load"
                onClicked: {
                    open_file_dialog.visible = true
                }
            }
            ToolButton {
                anchors.top: parent.top
                anchors.bottom: parent.bottom
                text: "Export"
                onClicked: {
                    export_file_dialog.visible = true
                }
            }
        }
    }

    CutToolList {
        id: cut_tools
        anchors.top: toolbar.bottom

        onHeightChanged: {
            connections.requestPaint();
        }
    }

    JobConnections {
        id: connections
        anchors.top: toolbar.bottom
        anchors.left: parent.left
        anchors.leftMargin: cut_tools.width
        anchors.right: documents.right
    }

    DocumentList {
        id: documents
        anchors.top: toolbar.bottom
        anchors.left: parent.left
        anchors.leftMargin: 250
        width: 200

        onHeightChanged: {
            connections.requestPaint();
        }
    }

    FileDialog {
        id: open_file_dialog
        title: "Please choose a file"
        selectMultiple: true
        nameFilters: NK3.Application.getLoadFileTypes()

        onAccepted: {
            for(var idx in fileUrls)
            {
                NK3.Application.loadFile(fileUrls[idx]);
            }
        }
    }

    FileDialog {
        id: export_file_dialog
        title: "Please choose a file"
        nameFilters: ["GCode files (*.gcode *.nc *.g)"]
        selectExisting: false

        onAccepted: {
            NK3.Application.exportFile(fileUrls[0]);
        }
    }
}
