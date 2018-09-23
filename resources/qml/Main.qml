import QtQuick 2.2
import QtQuick.Controls 1.0
import QtQuick.Layouts 1.0
import QtQuick.Dialogs 1.0
import NK3 1.0

MainWindow {
    visible: true
    width: 640
    height: 480
    title: qsTr("NinjaKittens 3")

    MouseHandler {
        anchors.fill: parent
    }

    CutToolList {
        id: cut_tools
        anchors.top: parent.top

        onHeightChanged: {
            connections.requestPaint();
        }
    }

    JobConnections {
        id: connections
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.leftMargin: cut_tools.width
        anchors.right: documents.right
    }

    DocumentList {
        id: documents
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.leftMargin: 250
        width: 200

        onHeightChanged: {
            connections.requestPaint();
        }
    }
}
