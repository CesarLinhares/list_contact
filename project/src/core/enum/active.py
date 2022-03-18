from enum import Enum


class ActiveCondition(Enum):
    ACTIVE: dict = {'active': True}
    INACTIVE: dict = {'active': False}
