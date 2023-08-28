from PyQt5.QtCore import QPoint

from nk3.machine.outputmethod import OutputMethod
from nk3.qt.QObjectBase import qtSlot, QProperty
from nk3.settingType import SettingType
from ._machineCommThread import MachineCommThread


class MachineComm(OutputMethod):
    NAME = "Machine Comm"

    def __init__(self) -> None:
        super().__init__([
            SettingType(key="start_code", label="Start GCode", type="gcode", default="",
                        tooltip="""GCode that is inserted before the actual instructions to
                        generate the object. Things to prepare the machine can be put here,
                        like spinning up your spindle, setting coordinate systems."""),
            SettingType(key="end_code", label="End GCode", type="gcode", default="",
                        tooltip="""GCode that is inserted at the end of the instructions.
                        You can place code here to wind or disable your machine.
                        For example disabling motors, spindles."""),
        ])
        self.setLocalQmlSource("MachineComm.qml")

        self.__thread = MachineCommThread()
        self.__thread.onStatusUpdate.connect(self._onStatusUpdate)
        self.__thread.start()

    def _onStatusUpdate(self, status: str, connected: bool, busy: bool) -> None:
        self.status = status
        self.connected = connected
        self.busy = busy

    @qtSlot
    def start(self) -> None:
        start_code = self.getSettingValue("start_code").strip()
        if start_code != "":
            for line in start_code.split("\n"):
                self.__thread.queue(line)
        for move in self.getMoves():
            self.__thread.queue("G1 F%d X%.3f Y%.3f Z%.3f" % (move.speed, move.xy.real, move.xy.imag, move.z))
        end_code = self.getSettingValue("end_code").strip()
        if end_code != "":
            for line in end_code.split("\n"):
                self.__thread.queue(line)

    @qtSlot
    def abort(self) -> None:
        self.__thread.abort()

    @qtSlot
    def jog(self, x: float, y: float, z: float) -> None:
        self.__thread.jog(x, y, z)

    @qtSlot
    def zero(self, axis: str) -> None:
        self.__thread.zero(axis)

    @qtSlot
    def rawCommand(self, cmd: str) -> None:
        if cmd:
            self.__thread.queue(cmd)

    @qtSlot
    def moveToRequest(self, pos: QPoint) -> bool:
        print(pos)
        if not self.connected or self.busy:
            return False
        self.__thread.queue(f"G0 X{pos.x()} Y{pos.y()}")
        return True
