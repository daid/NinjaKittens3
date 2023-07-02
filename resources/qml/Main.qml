import QtQuick 2.2
import QtQuick.Controls 1.0
import QtQuick.Layouts 1.0
import QtQuick.Dialogs 1.2
import NK3 1.0 as NK3


NK3.MainWindow {
    visible: true
    title: qsTr("NinjaKittens 3")

    function setOrigin(x, y) {
        for(var idx=0; idx<document_list.size(); idx++)
            document_list.get(idx).setOrigin(x, y);
        NK3.Application.home()
    }

    function transformDocuments(xx, xy, yx, yy) {
        for(var idx=0; idx<document_list.size(); idx++)
            document_list.get(idx).transform(xx, xy, yx, yy);
        NK3.Application.home()
    }

    Menu {
        id: contextMenu
        Menu {
            title: "Rotate"
            MenuItem { text: "Left 90 degree"; onTriggered: { transformDocuments(0, -1, 1, 0); } }
            MenuItem { text: "Right 90 degree"; onTriggered: { transformDocuments(0, 1, -1, 0); } }
        }
        Menu {
            title: "Mirror"
            MenuItem { text: "X"; onTriggered: { transformDocuments(-1, 0, 0, 1); } }
            MenuItem { text: "Y"; onTriggered: { transformDocuments(1, 0, 0, -1); } }
        }
        Menu {
            title: "Origin"
            MenuItem { text: "Front Left"; onTriggered: { setOrigin(0, 0); } }
            MenuItem { text: "Front Center"; onTriggered: { setOrigin(0.5, 0); } }
            MenuItem { text: "Front Right"; onTriggered: { setOrigin(1, 0); } }
            MenuItem { text: "Center Left"; onTriggered: { setOrigin(0, 0.5); } }
            MenuItem { text: "Center Center"; onTriggered: { setOrigin(0.5, 0.5); } }
            MenuItem { text: "Center Right"; onTriggered: { setOrigin(1, 0.5); } }
            MenuItem { text: "Back Left"; onTriggered: { setOrigin(0, 1); } }
            MenuItem { text: "Back Center"; onTriggered: { setOrigin(0.5, 1); } }
            MenuItem { text: "Back Right"; onTriggered: { setOrigin(1, 1); } }
        }
    }

    NK3.MouseHandler {
        anchors.fill: parent
        onRightClick: {
            contextMenu.popup();
        }
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
        anchors.right: parent.right

        id: output_method_loader
        source: output_method.qml_source
    }

    Text {
        anchors.top: output_method_loader.bottom
        anchors.right: parent.right
        text: NK3.Application.result_info
    }
}
