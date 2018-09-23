import QtQuick 2.1
import QtQuick.Layouts 1.1

Column {
    spacing: 1
    Repeater {
        model: document_list
        delegate: DocumentNode {
        }
    }
}
