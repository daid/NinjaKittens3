import QtQuick 2.1
import QtQuick.Layouts 1.1

Column {
    spacing: 1
    Repeater {
        model: cut_tool_list
        CutToolItem {
        }
    }
}