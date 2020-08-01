import warnings

from sc2 import UnitTypeId, AbilityId
from sc2.ids.buff_id import BuffId
from sc2.unit import Unit, UnitOrder

from sharpy.plans.acts.act_base import ActBase


class ShieldOvercharge(ActBase):
    # shield overcharge to defend base
    def __init__(self):
        super().__init__()

    async def start(self, knowledge: "Knowledge"):
        await super().start(knowledge)

    async def execute(self) -> bool:
        for battery in self.cache.own(UnitTypeId.SHIELDBATTERY).ready:  # type: Unit
            if battery.energy <= 20:
                if not battery.has_buff(BuffId.NEXUSSHIELDOVERCHARGE):
                    nexus = self.cache.own(UnitTypeId.NEXUS).closest_to(battery)
                    if nexus.distance_to(battery) <= 8:
                        self.do(nexus(AbilityId.BATTERYOVERCHARGE_BATTERYOVERCHARGE, battery))
        return True
