import enum


class ProtossFirstStageStrategyId(enum.Enum):
    VCTECHNOLOGYLINE = 1
    VSTECHNOLOGYLINE = 2
    VRTECHNOLOGYLINE = 3
    WILDBASEUNKNOWN = 4
    UNKNOWNTECHLINE = 5
    def __repr__(self):
        return f"ProtossFirstStageStrategyId.{self.name}"

class ProtossStartUpStrategyId(enum.Enum):
    ECOSTARTUP = 1
    TWOBGSTARTUP = 2
    THREEBGSTARTUP = 3
    ONEBGTECH = 4
    UNKNOWNSTARTUPSTRATEGY = 5
    def __repr__(self):
        return f"ProtossStartUpStrategyId.{self.name}"

for item in ProtossFirstStageStrategyId:
    assert not item.name in globals()
    globals()[item.name] = item

for item in ProtossStartUpStrategyId:
    assert not item.name in globals()
    globals()[item.name] = item