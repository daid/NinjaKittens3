import QtQuick 2.15
import QtQuick.Controls 1.0
import QtQuick.Layouts 1.0
import QtQuick.Dialogs 1.0
import NK3 1.0 as NK3


Rectangle {
    width: childrenRect.width
    implicitHeight: childrenRect.height

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
                    {value: 100, text: "100mm"},
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
                onAccepted: {
                    if (output_method.connected && !output_method.busy) output_method.rawCommand(rawinput.text);
                }
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
                var mode = jog_mode.model[jog_mode.currentIndex].value;
                if (mode != 0 && output_method.connected && !output_method.busy)
                    output_method.jog(-mode, 0, 0);
            }
        }
        Shortcut {
            sequences: ["Right", "d"]
            onActivated: {
                var mode = jog_mode.model[jog_mode.currentIndex].value;
                if (mode != 0 && output_method.connected && !output_method.busy)
                    output_method.jog(mode, 0, 0);
            }
        }
        Shortcut {
            sequences: ["Up", "w"]
            onActivated: {
                var mode = jog_mode.model[jog_mode.currentIndex].value;
                if (mode != 0 && output_method.connected && !output_method.busy)
                    output_method.jog(0, mode, 0);
            }
        }
        Shortcut {
            sequences: ["Down", "s"]
            onActivated: {
                var mode = jog_mode.model[jog_mode.currentIndex].value;
                if (mode != 0 && output_method.connected && !output_method.busy)
                    output_method.jog(0, -mode, 0);
            }
        }
        Shortcut {
            sequences: ["e"]
            onActivated: {
                var mode = jog_mode.model[jog_mode.currentIndex].value;
                if (mode != 0 && output_method.connected && !output_method.busy)
                    output_method.jog(0, 0, mode);
            }
        }
        Shortcut {
            sequences: ["q"]
            onActivated: {
                var mode = jog_mode.model[jog_mode.currentIndex].value;
                if (mode != 0 && output_method.connected && !output_method.busy)
                    output_method.jog(0, 0, -mode);
            }
        }
    }
}
