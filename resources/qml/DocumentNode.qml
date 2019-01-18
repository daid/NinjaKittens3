import QtQuick 2.1
import QtQuick.Controls 1.0
import QtQuick.Layouts 1.1

Component {
    id: document_node
    Column {
        x: 10
        Row {
            spacing: 2
            height: 20
            Rectangle {
                width: parent.height
                height: parent.height
                border.width: 1
                radius: 7

                MouseArea {
                    anchors.fill: parent
                    cursorShape: Qt.DragLinkCursor
                    onPressed: {
                        connections.dragging = item
                    }
                    onPositionChanged: {
                        connections.drag_target = parent.mapToItem(connections, mouse.x, mouse.y)
                        connections.requestPaint();
                    }
                    onReleased: {
                        connections.dragging = null
                        connections.requestPaint();

                        for(var i=0; i<cut_tools.children.length; i++)
                        {
                            var child = cut_tools.children[i]
                            var p = mapToItem(child, mouse.x, mouse.y)
                            if (child.contains(Qt.point(p.x, p.y)))
                            {
                                for(var j=0; j<child.operations.children.length; j++)
                                {
                                    var child2 = child.operations.children[j];
                                    var p = mapToItem(child2, mouse.x, mouse.y)
                                    if (child2.contains(Qt.point(p.x, p.y)))
                                    {
                                        item.tool_index = i;
                                        item.operation_index = j;
                                        return;
                                    }
                                }
                            }
                        }
                        item.tool_index = -1;
                        item.operation_index = -1;
                    }
                }
            }
            Text {
                height: parent.height
                horizontalAlignment: Text.AlignLeft
                verticalAlignment: Text.AlignVCenter
                text: item.name
            }
        }

        Repeater {
            model: item
            Loader {
                property var item: model.item
                sourceComponent: document_node
                onLoaded: print("Loaded:", item, item.name, item.size())
            }
        }
    }
}
