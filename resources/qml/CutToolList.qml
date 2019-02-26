import QtQuick 2.1
import QtQuick.Controls 1.0
import QtQuick.Layouts 1.1
import NK3 1.0 as NK3


Column {
    spacing: 1
    Repeater {
        model: NK3.Application.active_machine.tools
        CutToolItem {
        }
    }
}
