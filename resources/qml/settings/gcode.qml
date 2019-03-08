import QtQuick 2.1
import QtQuick.Controls 1.0
import QtQuick.Layouts 1.1

TextArea {
    text: setting.value
    wrapMode: TextEdit.NoWrap
    Keys.onReleased: {
        setting.value = text
    }
    onEditingFinished: {
        setting.value = text
    }
}
