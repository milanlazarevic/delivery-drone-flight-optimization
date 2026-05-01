from enum import Enum


class CommandNames(str, Enum):
    ARM_UP = "create-node"
    TAKE_OFF = "take-off"
    GO_TO = "go-to"
    LAND = "land"
    RETURN_HOME = "return-to-home"
    MISSION_CLEAR_ALL = "clear-mission"
    MISSION_UPLOAD = "upload-mission"
