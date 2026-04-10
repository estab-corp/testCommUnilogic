from enum import IntEnum
from typing import Tuple


class ValidationType(IntEnum):
    PICK_AND_PLACE = 0  # VTD
    DEPOSE_RETOURNEUR = 1  # VTDBRE
    PRISE_RETOURNEUR = 2  # VTPBRE


class MoveRequest:
    def __init__(self, typ: ValidationType, origin: Tuple[int, int, int], dest: Tuple[int, int, int], task_id: int):
        self.typ = typ
        self.origin = origin
        self.dest = dest
        self.task_id = task_id

    def __repr__(self) -> str:
        return f"typ={self.typ} origin={self.origin} dest={self.dest} task_id={self.task_id}"


class RxBaseMsg:
    pass


class TaskStartedMsg(RxBaseMsg):
    def __init__(self, task_id: int, ok_status: int) -> None:
        super().__init__()
        self.task_id = task_id
        self.ok_status = ok_status

    def __repr__(self) -> str:
        return f"TaskStartedMsg: task_id={self.task_id} ok_status={self.ok_status}"


class TaskEndedMsg(RxBaseMsg):
    def __init__(self, task_id: int, ok_status: int) -> None:
        super().__init__()
        self.task_id = task_id
        self.ok_status = ok_status

    def __repr__(self) -> str:
        return f"TaskEndedMsg: task_id={self.task_id} ok_status={self.ok_status}"


class MachineStateMsg(RxBaseMsg):
    def __init__(self, test: int) -> None:
        self.test = test

    def __repr__(self) -> str:
        return f"MachineStateMsg: test={self.test}"
