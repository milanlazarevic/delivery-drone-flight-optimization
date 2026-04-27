from enum import Enum

class CommandStatus(Enum):
    PENDING   = "pending"
    SENT      = "sent"
    ACKED     = "acked"
    VALIDATING = "validating" 
    SUCCESS   = "success"
    FAILED    = "failed"
    TIMEOUT   = "timeout"