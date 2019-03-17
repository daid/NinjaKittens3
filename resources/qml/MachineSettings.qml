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
        ComboBox {
            width: 200
            model: NK3.Application.active_machine.output_methods
            currentIndex: model.indexOf(NK3.Application.active_machine.output_method.typename)
            onActivated: NK3.Application.active_machine.switchOutputMethod(model[index])
        }
        Repeater {
            model: NK3.Application.active_machine.output_method
            Setting {}
        }
    }
}
