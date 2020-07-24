from random import choice
from typing import Callable, Tuple, List, Dict, Optional

from sc2 import UnitTypeId
from sc2.ids.upgrade_id import UpgradeId
from sharpy.knowledges import KnowledgeBot
from sharpy.managers import ManagerBase, DataManager

# This imports all the usual components for protoss bots
from sharpy.managers.roles import UnitTask
from sharpy.plans.protoss import *

from sc2.unit import Unit


# This imports all the usual components for terran bots
# from sharpy.plans.terran import *

# This imports all the usual components for zerg bots
# from sharpy.plans.zerg import *

# python run_custom.py -m OdysseyLE -p1 pvpbot -p2 stalker


class ProtossBot(KnowledgeBot):
    data_manager: DataManager

    def __init__(self, build_name: str = "default"):
        super().__init__("EZ bot PVP")

        self.conceded = False

        self.builds: Dict[str, Callable[[], BuildOrder]] = {
            "eco_start_up": lambda: self.eco_build()
        }
        self.build_name = build_name

    def configure_managers(self) -> Optional[List[ManagerBase]]:
        # self.knowledge.roles.role_count = 11
        self.knowledge.roles.set_tag_each_iteration = True
        # Return your custom managers here:
        return None

    async def on_step(self, iteration):
        return await super().on_step(iteration)

    async def create_plan(self) -> BuildOrder:
        if self.build_name == "default":
            # self.build_name = choice(list(self.builds.keys()))
            self.build_name = "eco_start_up"

        self.knowledge.data_manager.set_build(self.build_name)
        return self.builds[self.build_name]()

    def eco_build(self) -> BuildOrder:
        return BuildOrder(
            self.two_BG_oracle_start_up(),
            self.main_force(),
            self.chrono_production(),
            self.create_common_strategy()
        )

    def create_common_strategy(self) -> SequentialList:
        return SequentialList(
            # Sets workers to work
            DistributeWorkers(),
            # Detects enemy units as hallucinations
            PlanHallucination(),
            # Cancels buildings that are about to go down
            PlanCancelBuilding(),
            # Set worker rally point
            WorkerRallyPoint(),
            # Have the combat units gather in one place
            PlanZoneGather(),
            OracleHarass(),
            DoubleAdeptScout(),
            # Defend
            ShieldOvercharge(),
            PlanZoneDefense(),
            # Attack, these 2 should be last in a sequential list in this order
            PlanZoneAttack(),
            PlanFinishEnemy()
        )

    def two_BG_oracle_start_up(self) -> SequentialList:
        return SequentialList(
            Workers(14),
            GridBuilding(unit_type=UnitTypeId.PYLON, to_count=1),
            Workers(15),
            GridBuilding(unit_type=UnitTypeId.GATEWAY, to_count=1),
            # Scout(unit_types=UnitTypeId.PROBE, unit_count=1),
            Workers(17),
            BuildGas(1),
            Workers(18),
            BuildGas(2),
            Workers(19),
            GridBuilding(unit_type=UnitTypeId.GATEWAY, to_count=2),
            Workers(21),
            GridBuilding(unit_type=UnitTypeId.CYBERNETICSCORE, to_count=1),
            Workers(22),
            GridBuilding(unit_type=UnitTypeId.PYLON, to_count=2),
            Workers(23),
            GridBuilding(unit_type=UnitTypeId.STARGATE, to_count=1),
            ProtossUnit(UnitTypeId.STALKER, 2, only_once=True),
            Tech(UpgradeId.WARPGATERESEARCH),
            GridBuilding(unit_type=UnitTypeId.PYLON, to_count=3),
            ProtossUnit(UnitTypeId.ORACLE, 1, only_once=True),
            Expand(2),
            GridBuilding(unit_type=UnitTypeId.PYLON, to_count=4),
            DefensiveCannons(to_count_pre_base=0, additional_batteries=2, to_base_index=1),
            GridBuilding(unit_type=UnitTypeId.ROBOTICSFACILITY, to_count=1),
        )

    def main_force(self) -> BuildOrder:
        return BuildOrder(
            AutoPylon(),
            AutoWorker(),
            StepBuildGas(3, skip_until=UnitReady(UnitTypeId.PROBE, 36)),
            StepBuildGas(4, skip_until=UnitReady(UnitTypeId.PROBE, 39)),
            ProtossUnit(UnitTypeId.STALKER),
            ProtossUnit(UnitTypeId.IMMORTAL),
            Step(UnitExists(UnitTypeId.ROBOTICSFACILITY), GridBuilding(unit_type=UnitTypeId.GATEWAY, to_count=4)),
            Step(Supply(70), GridBuilding(unit_type=UnitTypeId.ROBOTICSFACILITY, to_count=2)),
            Step(Supply(90), Expand(3, priority=True))
        )

    def chrono_production(self) -> BuildOrder:
        return BuildOrder(
            ChronoUnit(UnitTypeId.ORACLE, UnitTypeId.STARGATE, 1),
            ChronoUnit(UnitTypeId.STALKER, UnitTypeId.GATEWAY, 2),
            ChronoUnit(UnitTypeId.IMMORTAL, UnitTypeId.ROBOTICSFACILITY, 0)
        )
