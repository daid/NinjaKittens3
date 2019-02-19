import QtQuick 2.2
import QtQuick.Controls 1.0
import QtQuick.Layouts 1.0
import QtQuick.Dialogs 1.0

Canvas {
    height: parent.height
    contextType: "2d"
    id: connectionCanvas

    property var dragging: null
    property var drag_target: null
    
    function paintNode(node, target, parent)
    {
        if (node == dragging)
        {
            var source_pos = drag_target
            var target_pos = target.mapToItem(connectionCanvas, 0, 10)
            context.moveTo(source_pos.x, source_pos.y)
            context.bezierCurveTo((source_pos.x + target_pos.x) / 2, source_pos.y, (source_pos.x + target_pos.x) / 2, target_pos.y, target_pos.x, target_pos.y)
        }
        else if (node.tool_index > -1 && node.operation_index > -1)
        {
            var source = cut_tools.children[node.tool_index].operations.children[node.operation_index];
            var source_pos = source.mapToItem(connectionCanvas, source.width, 15)
            var target_pos = target.mapToItem(connectionCanvas, 0, 10)
            context.moveTo(source_pos.x, source_pos.y)
            context.bezierCurveTo((source_pos.x + target_pos.x) / 2, source_pos.y, (source_pos.x + target_pos.x) / 2, target_pos.y, target_pos.x, target_pos.y)
        }
        else if (parent != undefined)
        {
            var source_pos = parent.mapToItem(connectionCanvas, 0, 15)
            var target_pos = target.mapToItem(connectionCanvas, 0, 10)
            context.moveTo(source_pos.x, source_pos.y)
            context.bezierCurveTo(source_pos.x, (source_pos.y + target_pos.y) / 2, source_pos.x, target_pos.y, target_pos.x, target_pos.y)
        }
        else
        {
            var target_pos = target.mapToItem(connectionCanvas, 0, 10)
            context.moveTo(target_pos.x - 15, target_pos.y)
            context.lineTo(target_pos.x, target_pos.y)
        }
        for(var i=0; i<node.size(); i++)
            paintNode(node.get(i), target.children[i + 1].children[0], target)
    }

    onPaint:
    {
        if (context == null) return;
        context.reset();
        context.strokeStyle = Qt.rgba(0,0,0);
        context.beginPath()
        for(var i=0; i<document_list.size(); i++)
            paintNode(document_list.get(i), documents.children[i], undefined)
        context.stroke();
    }
}
