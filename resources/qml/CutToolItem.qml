import QtQuick 2.1
import QtQuick.Controls 1.0
import QtQuick.Layouts 1.1

Column {
    property Item operations: operations
    Item {
        property bool open: false
        clip: true

        implicitWidth: 200
        implicitHeight: open ? main.height : header.height
        Behavior on implicitHeight {
            PropertyAnimation { duration: 100 }
        }

        Column {
            id: main
            spacing: 1
            anchors.left: parent.left
            anchors.right: parent.right

            RowLayout {
                implicitHeight: 30
                id: header
                width: parent.width

                Text {
                    horizontalAlignment: Text.AlignRight
                    verticalAlignment: Text.AlignVCenter
                    Layout.fillHeight: true
                    text: "^"
                    rotation: parent.parent.parent.parent.open ? "180" : 0
                    Behavior on rotation {
                        PropertyAnimation { duration: 100 }
                    }
                    MouseArea {
                        anchors.fill: parent
                        cursorShape: Qt.PointingHandCursor
                        onClicked: {
                            parent.parent.parent.parent.open = !parent.parent.parent.parent.open;
                        }
                    }
                }

                TextField {
                    Layout.fillWidth: true
                    horizontalAlignment: Text.AlignLeft
                    verticalAlignment: Text.AlignVCenter
                    text: item.name
                    placeholderText: qsTr("Tool name")
                    Keys.onReleased: {
                        item.name = text
                    }
                    onEditingFinished: {
                        item.name = text
                    }
                }
            }

            Repeater {
                model: item
                Setting {}
            }
        }
    }
    Column {
        id: operations
        Repeater {
            model: item.operations
            OperationItem { x: 50 }
        }
    }
}