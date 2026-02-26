from enum import Enum, auto

class Mode(Enum):
    SELECT = auto()     
    TRANSFORM = auto()      
    EXPORT = auto()      
    CREATE = auto()  
    CREATE_LABEL = auto()