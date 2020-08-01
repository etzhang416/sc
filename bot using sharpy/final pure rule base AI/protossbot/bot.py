from random import choice
from typing import Callable, Tuple, List, Dict, Optional

from sc2 import UnitTypeId
from sc2 import Race
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

# python run_custom.py -m OdysseyLE -p1 protossbot -p2 stalker


class ProtossBot(KnowledgeBot):
    data_manager: DataManager

    def __init__(self, build_name: str = "default"):
        super().__init__("EZ bot PVP")

        self.conceded = False

        self.builds: Dict[str, Callable[[], BuildOrder]] = {
            "pvp": lambda: self.pvp_build(),
            "pvz": lambda: self.pvz_build(),
            "pvt": lambda: self.pvt_build()
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
            if self.knowledge.enemy_race == Race.Protoss:
                self.build_name = "pvp"
            elif self.knowledge.enemy_race == Race.Zerg:
                self.build_name = "pvz"
            elif self.knowledge.enemy_race == Race.Terran:
                self.build_name = "pvt"
            else:
                self.build_name = self.build_name = "pvz"

        self.knowledge.data_manager.set_build(self.build_name)
        return self.builds[self.build_name]()

    # these are pvp
    def pvp_build(self) -> BuildOrder:
        return BuildOrder(
            self.anti_clocked(),
            self.two_BG_oracle_start_up(),
            self.pvp_main_force(),
            self.pvp_main_tech(),
            self.pvp_chrono_production(),
            self.create_common_strategy()
        )

    def create_common_strategy(self) -> SequentialList:
        return SequentialList(
            # Sets workers to work
            ShieldOvercharge(),
            DistributeWorkers(),
            # Detects enemy units as hallucinations
            PlanHallucination(),
            HallucinatedPhoenixScout(),
            # Cancels buildings that are about to go down
            PlanCancelBuilding(),
            # Set worker rally point
            WorkerRallyPoint(),
            # Have the combat units gather in one place
            PlanZoneGather(),
            OracleHarass(),
            WarpPrismHarass(),
            DoubleAdeptScout(),
            # Defend
            PlanZoneDefense(),
            # Attack, these 2 should be last in a sequential list in this order
            PlanZoneAttack(),
            PlanFinishEnemy()
        )

    def two_BG_oracle_start_up(self) -> SequentialList:
        return SequentialList(
            Workers(14),
            GridBuilding(unit_type=UnitTypeId.PYLON, to_count=1, priority=True),
            Workers(15),
            GridBuilding(unit_type=UnitTypeId.GATEWAY, to_count=1, priority=True),
            # Scout(unit_types=UnitTypeId.PROBE, unit_count=1),
            Workers(17),
            BuildGas(1),
            Workers(18),
            BuildGas(2),
            Workers(19),
            GridBuilding(unit_type=UnitTypeId.GATEWAY, to_count=2, priority=True),
            Workers(21),
            GridBuilding(unit_type=UnitTypeId.CYBERNETICSCORE, to_count=1, priority=True),
            Workers(22),
            GridBuilding(unit_type=UnitTypeId.PYLON, to_count=2, priority=True),
            Workers(23),
            GridBuilding(unit_type=UnitTypeId.STARGATE, to_count=1, priority=True),
            ProtossUnit(UnitTypeId.STALKER, 2, only_once=True),
            Tech(UpgradeId.WARPGATERESEARCH),
            GridBuilding(unit_type=UnitTypeId.PYLON, to_count=3, priority=True),
            ProtossUnit(UnitTypeId.ORACLE, 1, only_once=True, priority=True),
            Expand(2),
            GridBuilding(unit_type=UnitTypeId.PYLON, to_count=4, priority=True),
            DefensiveCannons(to_count_pre_base=0, additional_batteries=1, to_base_index=1),
            GridBuilding(unit_type=UnitTypeId.ROBOTICSFACILITY, to_count=1, priority=True)
        )

    def pvp_main_force(self) -> BuildOrder:
        return BuildOrder(
            AutoPylon(),
            ProtossUnit(UnitTypeId.STALKER),
            ProtossUnit(UnitTypeId.IMMORTAL),
            Step(Supply(90), GridBuilding(unit_type=UnitTypeId.ROBOTICSFACILITY, to_count=2)),
            Step(Supply(100), Expand(3, priority=True)),
            Step(UnitExists(UnitTypeId.OBSERVER, include_killed=True),
                 ProtossUnit(UnitTypeId.IMMORTAL, to_count=4, priority=True)),
            Step(UnitExists(UnitTypeId.STALKER, count=10),
                 ProtossUnit(UnitTypeId.SENTRY, to_count=2)),
            Step(UnitExists(UnitTypeId.STALKER, count=14),
                 ProtossUnit(UnitTypeId.PHOENIX, to_count=1, priority=True)),
            Tech(UpgradeId.BLINKTECH),
            Step(UnitExists(UnitTypeId.ROBOTICSBAY),
                 ProtossUnit(UnitTypeId.DISRUPTOR, to_count=2, priority=True)),
            Step(UnitExists(UnitTypeId.FLEETBEACON),
                 ProtossUnit(UnitTypeId.MOTHERSHIP, to_count=1)),
            Step(UnitExists(UnitTypeId.FLEETBEACON),
                 ProtossUnit(UnitTypeId.TEMPEST, to_count=2, priority=True)),
        )

    def pvp_chrono_production(self) -> BuildOrder:
        return BuildOrder(
            ChronoUnit(UnitTypeId.ORACLE, UnitTypeId.STARGATE, 1),
            ChronoUnit(UnitTypeId.STALKER, UnitTypeId.GATEWAY, 1),
            ChronoUnit(UnitTypeId.IMMORTAL, UnitTypeId.ROBOTICSFACILITY),
            ChronoUnit(UnitTypeId.DISRUPTOR, UnitTypeId.ROBOTICSFACILITY),
            ChronoAnyTech(save_to_energy=100)
        )

    def anti_clocked(self) -> BuildOrder:
        return BuildOrder(
            Step(UnitExists(UnitTypeId.ROBOTICSFACILITY), ProtossUnit(UnitTypeId.OBSERVER, priority=True, to_count=1))
        )

    def pvp_main_tech(self) -> BuildOrder:
        return BuildOrder(
            AutoWorker(),
            StepBuildGas(3, skip_until=UnitReady(UnitTypeId.PROBE, 36)),
            StepBuildGas(4, skip_until=UnitReady(UnitTypeId.PROBE, 39)),
            StepBuildGas(6, skip_until=UnitReady(UnitTypeId.NEXUS, count=3)),
            Step(UnitExists(UnitTypeId.ROBOTICSFACILITY), GridBuilding(unit_type=UnitTypeId.GATEWAY, to_count=3)),
            Step(UnitExists(UnitTypeId.WARPGATE, count=3),
                 GridBuilding(unit_type=UnitTypeId.TWILIGHTCOUNCIL, to_count=1)),
            Step(Supply(86), GridBuilding(unit_type=UnitTypeId.FORGE, to_count=1)),
            Step(UnitExists(UnitTypeId.NEXUS, count=3),
                 GridBuilding(unit_type=UnitTypeId.ROBOTICSBAY, to_count=1)),
            Step(UnitExists(UnitTypeId.NEXUS, count=2),
                 GridBuilding(unit_type=UnitTypeId.GATEWAY, to_count=4)),
            Step(UnitExists(UnitTypeId.NEXUS, count=3),
                 GridBuilding(unit_type=UnitTypeId.GATEWAY, to_count=7)),
            Step(UnitExists(UnitTypeId.NEXUS, count=3),
                 GridBuilding(unit_type=UnitTypeId.FLEETBEACON, to_count=1)),

            Tech(UpgradeId.PROTOSSGROUNDARMORSLEVEL1),
            Tech(UpgradeId.PROTOSSGROUNDWEAPONSLEVEL1),
            Tech(UpgradeId.PROTOSSSHIELDSLEVEL1),
            Tech(UpgradeId.PROTOSSGROUNDARMORSLEVEL2),
            Tech(UpgradeId.PROTOSSGROUNDWEAPONSLEVEL2),
            Tech(UpgradeId.PROTOSSSHIELDSLEVEL2)
        )

    # these are pvz
    def pvz_build(self) -> BuildOrder:
        return BuildOrder(
            self.pvz_chrono_production(),
            # self.test(),
            self.pvz_wall_fast_expand(),
            self.anti_clocked(),
            AutoPylon(),
            self.pvz_main_force(),
            self.create_common_strategy()
        )

    def pvz_wall_fast_expand(self) -> SequentialList:
        return SequentialList(
            Workers(14),
            GridBuilding(unit_type=UnitTypeId.PYLON, to_count=1, priority=True),
            Workers(17),
            Expand(2, priority=True),
            GridBuilding(unit_type=UnitTypeId.GATEWAY, to_count=1, priority=True),
            Workers(18),
            BuildGas(1),
            Workers(19),
            BuildGas(2),
            Workers(20),
            GridBuilding(unit_type=UnitTypeId.GATEWAY, to_count=2, priority=True),
            Workers(22),
            GridBuilding(unit_type=UnitTypeId.CYBERNETICSCORE, to_count=1, priority=True),
            ProtossUnit(UnitTypeId.ZEALOT, 1, only_once=True, priority=True),
            Workers(27),
            ProtossUnit(UnitTypeId.ADEPT, 2, only_once=True, priority=True),
            ChronoUnit(UnitTypeId.ADEPT, UnitTypeId.GATEWAY, 1),
            Tech(UpgradeId.WARPGATERESEARCH),
            GridBuilding(unit_type=UnitTypeId.TWILIGHTCOUNCIL, to_count=1, priority=True),
            Workers(31),
            GridBuilding(unit_type=UnitTypeId.PYLON, to_count=3, priority=True),
            Workers(32),
            Tech(UpgradeId.BLINKTECH),
            Workers(34),
            GridBuilding(unit_type=UnitTypeId.GATEWAY, to_count=6, priority=True),
            Workers(38),
            GridBuilding(unit_type=UnitTypeId.PYLON, to_count=5, priority=True),
            ProtossUnit(UnitTypeId.STALKER, 6, only_once=True, priority=True),
            GridBuilding(unit_type=UnitTypeId.GATEWAY, to_count=8, priority=True),
        )

    def pvz_main_force(self) -> BuildOrder:
        return BuildOrder(
            AutoPylon(),
            AutoWorker(),
            Step(Supply(70),
                 GridBuilding(unit_type=UnitTypeId.ROBOTICSFACILITY, to_count=1)),
            Step(Supply(100),
                 GridBuilding(unit_type=UnitTypeId.TEMPLARARCHIVE, to_count=1)),
            Step(Supply(80),
                 ProtossUnit(UnitTypeId.WARPPRISM, to_count=1, priority=True)),
            Step(Supply(108),
                 Expand(3, priority=True)),
            Step(Minerals(600), ProtossUnit(UnitTypeId.ZEALOT)),
            Step(UnitExists(UnitTypeId.ZEALOT, 6), Tech(UpgradeId.CHARGE)),
            Tech(UpgradeId.PSISTORMTECH),
            StepBuildGas(requirement=UnitExists(UnitTypeId.STALKER, 10), to_count=4),
            ProtossUnit(UnitTypeId.HIGHTEMPLAR),
            Step(UnitExists(UnitTypeId.HIGHTEMPLAR, 5), Archon(allowed_types=[UnitTypeId.HIGHTEMPLAR])),
            ProtossUnit(UnitTypeId.ADEPT, to_count=4, priority=True),
            ProtossUnit(UnitTypeId.STALKER, to_count=12, priority=True),
            ProtossUnit(UnitTypeId.IMMORTAL, to_count=4, priority=True)
        )

    def pvz_chrono_production(self) -> BuildOrder:
        return BuildOrder(
            ChronoUnit(UnitTypeId.ADEPT, UnitTypeId.GATEWAY, 1),
            ChronoUnit(UnitTypeId.IMMORTAL, UnitTypeId.ROBOTICSFACILITY),
            ChronoAnyTech(save_to_energy=100)
        )

    # these are pvz
    def pvt_build(self) -> BuildOrder:
        return BuildOrder(
            self.pvt_chrono_production(),
            self.pvt_two_BG_start_up(),
            self.anti_clocked(),
            self.pvt_main_force(),
            self.create_common_strategy()
        )

    def pvt_two_BG_start_up(self) -> SequentialList:
        return SequentialList(
            Workers(14),
            GridBuilding(unit_type=UnitTypeId.PYLON, to_count=1, priority=True),
            Workers(15),
            GridBuilding(unit_type=UnitTypeId.GATEWAY, to_count=1, priority=True),
            Workers(16),
            GridBuilding(unit_type=UnitTypeId.GATEWAY, to_count=2, priority=True),
            BuildGas(1),
            Workers(19),
            GridBuilding(unit_type=UnitTypeId.CYBERNETICSCORE, to_count=1, priority=True),
            GridBuilding(unit_type=UnitTypeId.PYLON, to_count=2, priority=True),
            Expand(2, priority=True),
            ProtossUnit(UnitTypeId.ADEPT, to_count=2, priority=True, only_once=True),
            ProtossUnit(UnitTypeId.STALKER, to_count=2, priority=True, only_once=True),
            DefensiveCannons(to_count_pre_base=0, additional_batteries=1, to_base_index=1),
            BuildGas(2),
            Workers(22),
            Tech(UpgradeId.WARPGATERESEARCH),
            GridBuilding(unit_type=UnitTypeId.ROBOTICSFACILITY, to_count=1, priority=True),
            Workers(26),
            ProtossUnit(UnitTypeId.IMMORTAL, to_count=1, priority=True, only_once=True),
            ProtossUnit(UnitTypeId.SENTRY, to_count=1, priority=True, only_once=True),
            GridBuilding(unit_type=UnitTypeId.ROBOTICSFACILITY, to_count=2, priority=True),
            GridBuilding(unit_type=UnitTypeId.GATEWAY, to_count=5, priority=True),
        )

    def pvt_main_force(self) -> BuildOrder:
        return BuildOrder(
            AutoPylon(),
            AutoWorker(),
            Step(Supply(64),
                 GridBuilding(unit_type=UnitTypeId.TWILIGHTCOUNCIL, to_count=1)),
            Step(Supply(76),
                 ProtossUnit(UnitTypeId.WARPPRISM, to_count=1, priority=True, only_once=True)),
            Step(Supply(90),
                 GridBuilding(unit_type=UnitTypeId.TEMPLARARCHIVE, to_count=1)),
            Step(Supply(108),
                 Expand(3, priority=True)),
            Step(Gas(300),
                 GridBuilding(unit_type=UnitTypeId.TEMPLARARCHIVE, to_count=1, priority=True)),
            ProtossUnit(UnitTypeId.ZEALOT, to_count=8),
            ProtossUnit(UnitTypeId.IMMORTAL, to_count=3, priority=True),
            ProtossUnit(UnitTypeId.SENTRY, 2, priority=True),
            ProtossUnit(UnitTypeId.STALKER, to_count=8, priority=True),
            ProtossUnit(UnitTypeId.HIGHTEMPLAR),
            Step(Minerals(400), ProtossUnit(UnitTypeId.ZEALOT)),
            Step(UnitExists(UnitTypeId.ZEALOT, 6), Tech(UpgradeId.CHARGE)),
            Tech(UpgradeId.PSISTORMTECH),
            StepBuildGas(requirement=Supply(70), to_count=4),
            Step(UnitExists(UnitTypeId.HIGHTEMPLAR, 5), Archon(allowed_types=[UnitTypeId.HIGHTEMPLAR])),
            Step(UnitExists(UnitTypeId.STALKER, 7), ProtossUnit(UnitTypeId.IMMORTAL, to_count=6, priority=True))
        )

    def pvt_chrono_production(self) -> BuildOrder:
        return BuildOrder(
            ChronoUnit(UnitTypeId.ADEPT, UnitTypeId.GATEWAY, 1),
            ChronoUnit(UnitTypeId.IMMORTAL, UnitTypeId.ROBOTICSFACILITY),
            ChronoAnyTech(save_to_energy=100)
        )

    def test(self) -> SequentialList:
        return SequentialList(
            Workers(14),
            GridBuilding(unit_type=UnitTypeId.PYLON, to_count=1, priority=True),
            Workers(15),
            GridBuilding(unit_type=UnitTypeId.GATEWAY, to_count=1, priority=True),
            Workers(16),
            BuildGas(1),
            Workers(19),
            GridBuilding(unit_type=UnitTypeId.GATEWAY, to_count=2, priority=True),
            ProtossUnit(UnitTypeId.ZEALOT, to_count=1, priority=True, only_once=True),
            BuildGas(2),
            GridBuilding(unit_type=UnitTypeId.CYBERNETICSCORE, to_count=1, priority=True),
            GridBuilding(unit_type=UnitTypeId.PYLON, to_count=2, priority=True),
            Workers(22),
            ProtossUnit(UnitTypeId.ADEPT, to_count=2, priority=True, only_once=True),
            ProtossUnit(UnitTypeId.STALKER, to_count=2, priority=True, only_once=True),
            Expand(2, priority=True),
            DefensiveCannons(to_count_pre_base=0, additional_batteries=1, to_base_index=1),
            Tech(UpgradeId.WARPGATERESEARCH),
            GridBuilding(unit_type=UnitTypeId.ROBOTICSFACILITY, to_count=1, priority=True),
            Workers(26),
            ProtossUnit(UnitTypeId.IMMORTAL, to_count=1, priority=True, only_once=True),
            ProtossUnit(UnitTypeId.SENTRY, to_count=1, priority=True, only_once=True),
            ProtossUnit(UnitTypeId.WARPPRISM, to_count=1, priority=True, only_once=True),
            GridBuilding(unit_type=UnitTypeId.GATEWAY, to_count=5, priority=True),
        )