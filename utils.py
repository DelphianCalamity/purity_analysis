from enum import Enum


class StoreOp(Enum):
    ATTR = 'STORE_ATTR'
    DEREF = 'STORE_DEREF'
    FAST = 'STORE_FAST'
    GLOBAL = 'STORE_GLOBAL'
    NAME = 'STORE_NAME'
    SUBSCR = 'STORE_SUBSCR'
