import QtQuick 2.2
import QtQuick.Controls 1.0
import QtQuick.Layouts 1.0
import QtQuick.Dialogs 1.2
import NK3 1.0 as NK3


Dialog {
    title: "Machine settings"

    Column {
        Repeater {
            model: NK3.Application.active_machine
            Setting {}
        }
        Repeater {
            model: NK3.Application.active_machine.export
            Setting {}
        }
    }
}
