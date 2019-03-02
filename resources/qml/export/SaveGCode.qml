import QtQuick 2.2
import QtQuick.Controls 1.0
import QtQuick.Layouts 1.0
import QtQuick.Dialogs 1.0
import NK3 1.0 as NK3


FileDialog {
    id: export_file_dialog
    title: "Please choose a file"
    nameFilters: ["GCode files (*.gcode *.nc *.g)"]
    selectExisting: false

    onAccepted: {
        print(fileUrls[0])
        NK3.Application.active_machine.export.save(fileUrls[0]);
    }
}