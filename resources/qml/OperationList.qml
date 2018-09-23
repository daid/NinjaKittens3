import QtQuick 2.1
import QtQuick.Layouts 1.1

ColumnLayout {
    spacing: 1
    Repeater {
        model: job_operation_list
        OperationItem {
        }
    }
}