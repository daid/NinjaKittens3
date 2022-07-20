import QtQuick 2.15
import QtQuick.Controls 1.0
import QtQuick.Layouts 1.0
import QtQuick.Dialogs 1.0
import QtQuick.Shapes 1.0
import NK3 1.0 as NK3


Item {
    Rectangle {
        width: childrenRect.width
        implicitHeight: childrenRect.height
        anchors.right: parent.right

        ColumnLayout {
            id: content

            Text {
                text: output_method.status;
            }
            RowLayout {
                Text { text: "Jog:" }
                ComboBox {
                    id: jog_mode
                    model: [
                        {value: 0, text: "None"},
                        {value: 10, text: "10mm"},
                        {value: 1, text: "1mm"},
                        {value: 0.1, text: "0.1mm"}
                    ]
                }
                Button {
                    text: "Run job"
                    onClicked: output_method.start();
                    enabled: output_method.connected && !output_method.busy
                }
                Button {
                    text: "Abort"
                    onClicked: output_method.abort();
                    enabled: output_method.connected && output_method.busy
                }
            }
            RowLayout {
                Text { text: "Zero:" }
                Button {
                    text: "X"
                    onClicked: output_method.zero("X");
                    enabled: output_method.connected && !output_method.busy
                }
                Button {
                    text: "Y"
                    onClicked: output_method.zero("Y");
                    enabled: output_method.connected && !output_method.busy
                }
                Button {
                    text: "Z"
                    onClicked: output_method.zero("Z");
                    enabled: output_method.connected && !output_method.busy
                }
            }
            RowLayout {
                TextField {
                    Layout.fillWidth: true
                    id: rawinput
                }
                Button {
                    text: "Send"
                    onClicked: output_method.rawCommand(rawinput.text);
                    enabled: output_method.connected && !output_method.busy
                }
            }

            Shortcut {
                sequences: ["Left", "a"]
                onActivated: {
                    if (jog_mode.currentValue != 0 && output_method.connected && !output_method.busy)
                        output_method.jog(-jog_mode.currentValue, 0, 0);
                }
            }
            Shortcut {
                sequences: ["Right", "d"]
                onActivated: {
                    if (jog_mode.currentValue != 0 && output_method.connected && !output_method.busy)
                        output_method.jog(jog_mode.currentValue, 0, 0);
                }
            }
            Shortcut {
                sequences: ["Up", "w"]
                onActivated: {
                    if (jog_mode.currentValue != 0 && output_method.connected && !output_method.busy)
                        output_method.jog(0, jog_mode.currentValue, 0);
                }
            }
            Shortcut {
                sequences: ["Down", "s"]
                onActivated: {
                    if (jog_mode.currentValue != 0 && output_method.connected && !output_method.busy)
                        output_method.jog(0, -jog_mode.currentValue, 0);
                }
            }
            Shortcut {
                sequences: ["e"]
                onActivated: {
                    if (jog_mode.currentValue != 0 && output_method.connected && !output_method.busy)
                        output_method.jog(0, 0, jog_mode.currentValue);
                }
            }
            Shortcut {
                sequences: ["q"]
                onActivated: {
                    if (jog_mode.currentValue != 0 && output_method.connected && !output_method.busy)
                        output_method.jog(0, 0, -jog_mode.currentValue);
                }
            }
        }
    }
}