import QtQuick 2.2
import QtQuick.Controls 1.0
import QtQuick.Layouts 1.0
import QtQuick.Dialogs 1.2
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
                text: "Edit machine settings"
                onClicked: machine_settings.open()
            }
            ToolButton {
                anchors.top: parent.top
                anchors.bottom: parent.bottom
                text: "[Reload QML]"
                onClicked: {
                    NK3.Application.reloadQML();
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

    MachineSettings {
        id: machine_settings
    }

    Loader {
        anchors.top: toolbar.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom

        id: output_method_loader
        source: output_method.qml_source
    }
}
