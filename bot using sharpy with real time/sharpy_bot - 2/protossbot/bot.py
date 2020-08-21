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
from sharpy.managers.build_detector import EnemyRushBuild


# This imports all the usual components for terran bots
# from sharpy.plans.terran import *

# This imports all the usual components for zerg bots
# from sharpy.plans.zerg import *

# python run_custom.py -m OdysseyLE -p1 protossbot -p2 4gate


class ProtossBot(KnowledgeBot):
    data_manager: DataManager

    def __init__(self, build_name: str = "default"):
        super().__init__("EZ bot PVP")

        self.conceded = False

        self.builds: Dict[str, Callable[[], BuildOrder]] = {
            "pvp": lambda: self.pvp_build(),
            "pvz": lambda: self.pvz_build(),
            "pvt": lambda: self.pvt_build(),
            "pvr": lambda: self.pvr_build()
        }
        self.build_name = build_name
        self.enemy_last_intel = None
        self.enemy_intel = None

    def configure_managers(self) -> Optional[List[ManagerBase]]:
        # self.knowledge.roles.role_count = 11
        self.knowledge.roles.set_tag_each_iteration = True
        # Return your custom managers here:
        return None

    async def on_step(self, iteration):
        self.enemy_intel = self.knowledge.build_detector.rush_build

        if self.enemy_last_intel is None:
            self.enemy_last_intel = self.enemy_intel

        if self.enemy_last_intel != self.enemy_intel:
            str = "Looks like you wanna "
            str += self.enemy_intel.name
            self.enemy_last_intel = self.enemy_intel
            await self.chat_send(str)
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
                self.build_name = self.build_name = "pvr"

        self.knowledge.data_manager.set_build(self.build_name)
        return self.builds[self.build_name]()

    def pvz_build(self) -> BuildOrder:
        return BuildOrder(
            self.pvz_main_force(),
            self.pvz_create_common_strategy()
        )

    def pvt_build(self) -> BuildOrder:
        return BuildOrder(
            self.pvt_main_force(),
            self.pvt_create_common_strategy()
        )

    # these are pvp
    def pvp_build(self) -> BuildOrder:
        return BuildOrder(
            self.pvp_main_force(),
            self.pvp_create_common_strategy()
        )

    # these are pvr
    def pvr_build(self) -> BuildOrder:
        return BuildOrder(
            self.pvr_main_force(),
            self.pvz_create_common_strategy()
        )

    def pvp_create_common_strategy(self) -> SequentialList:

        return SequentialList(
            ShieldOvercharge(),
            DistributeWorkers(),
            PlanHallucination(),
            HallucinatedPhoenixScout(),
            PlanCancelBuilding(),
            WorkerRallyPoint(),
            PlanZoneGather(),
            OracleHarass(),
            DoubleAdeptScout(adepts_to_start=6),
            PlanZoneDefense(),
            PlanZoneAttack(),
            PlanFinishEnemy()
        )

    def pvz_create_common_strategy(self) -> SequentialList:

        return SequentialList(
            ShieldOvercharge(),
            DistributeWorkers(),
            PlanHallucination(),
            HallucinatedPhoenixScout(),
            PlanCancelBuilding(),
            WorkerRallyPoint(),
            PlanZoneGather(),
            DoubleAdeptScout(adepts_to_start=8),
            OracleHarass(),
            PlanZoneDefense(),
            PlanZoneAttack(start_attack_power=16),
            PlanFinishEnemy()
        )

    def pvt_create_common_strategy(self) -> SequentialList:

        return SequentialList(
            ShieldOvercharge(),
            DistributeWorkers(),
            PlanHallucination(),
            HallucinatedPhoenixScout(),
            PlanCancelBuilding(),
            WorkerRallyPoint(),
            PlanZoneGather(),
            OracleHarass(),
            DoubleAdeptScout(adepts_to_start=1),
            PlanZoneDefense(),
            PlanZoneAttack(),
            PlanFinishEnemy()
        )

    # TODO: these are pvp related functions
    def pvp_main_force(self) -> BuildOrder:
        return BuildOrder(
            AutoWorker(),
            AutoPylon(),
            Step(lambda k: k.build_detector.rush_build == EnemyRushBuild.Macro, self.pvp_micro()),
            Step(lambda k: k.build_detector.rush_build == EnemyRushBuild.SafeExpand, self.pvp_micro()),

            Step(lambda k: k.build_detector.rush_build == EnemyRushBuild.WorkerRush, self.counter_ProxyZealots()),
            Step(lambda k: k.build_detector.rush_build == EnemyRushBuild.ProxyZealots, self.counter_ProxyZealots()),

            Step(lambda k: k.build_detector.rush_build == EnemyRushBuild.CannonRush, self.counter_CannonRush()),

            Step(lambda k: k.build_detector.rush_build == EnemyRushBuild.ProxyBase, self.counter_4BG()),
            Step(lambda k: k.build_detector.rush_build == EnemyRushBuild.Zealots, self.counter_4BG()),
            Step(lambda k: k.build_detector.rush_build == EnemyRushBuild.AdeptRush, self.counter_4BG()),

            Step(lambda k: k.build_detector.rush_build == EnemyRushBuild.AirOneBase, self.counter_air()),

            Step(lambda k: k.build_detector.rush_build == EnemyRushBuild.ProxyRobo, self.counter_Robo()),
            Step(lambda k: k.build_detector.rush_build == EnemyRushBuild.RoboRush, self.counter_Robo()),

            Step(lambda k: k.build_detector.rush_build == EnemyRushBuild.EarlyExpand, self.counter_EarlyExpand()),

            Step(lambda k: k.build_detector.rush_build == EnemyRushBuild.FastDT, self.counter_FastDT()),
        )

    def pvp_micro(self) -> BuildOrder:
        return BuildOrder(
            self.pvp_eco_start_up(),
            self.pvp_micro_build()
        )

    def pvp_eco_start_up(self) -> SequentialList:
        return SequentialList(
            Workers(13),
            GridBuilding(unit_type=UnitTypeId.PYLON, to_count=1, priority=True),
            Workers(14),
            GridBuilding(unit_type=UnitTypeId.GATEWAY, to_count=1, priority=True),
            # 0:40 enemy open worker rush build
            Step(UnitExists(UnitTypeId.NEXUS), action=ChronoUnit(UnitTypeId.PROBE, UnitTypeId.NEXUS, 1)),
            Workers(16),
            BuildGas(1),
            Workers(17),
            BuildGas(2),
            # 1:05 perfect time for detect enemy cannon rush at 2 nd base location
            Scout(UnitTypeId.PROBE, 1, ScoutLocation.scout_own2_behind()),
            Workers(18),
            ChronoUnit(UnitTypeId.PROBE, UnitTypeId.NEXUS, 1),
            Workers(19),
            GridBuilding(unit_type=UnitTypeId.GATEWAY, to_count=2, priority=True),
            # probe scout after 2BG
            # reach enemy base ramp at ~ 1:55
            # scout_main_2 is move around

            WorkerScout(),
            Workers(21),
            GridBuilding(unit_type=UnitTypeId.CYBERNETICSCORE, to_count=1, priority=True),
            Workers(22),
            GridBuilding(unit_type=UnitTypeId.PYLON, to_count=2, priority=True),

            Workers(23),
            Tech(UpgradeId.WARPGATERESEARCH),
            ProtossUnit(UnitTypeId.STALKER, 1, only_once=True, priority=True),
            ProtossUnit(UnitTypeId.SENTRY, 1, only_once=True, priority=True),
            ProtossUnit(UnitTypeId.STALKER, 2, only_once=True, priority=True),
            # my 2nd base ~ 2:45
            Expand(2),
            ProtossUnit(UnitTypeId.STALKER, 3, only_once=True),
            # 3 stalker+1sentry at ~ 3:20 for early adept
            # ~ 3:30 HallucinatedPhoenixScout reach enemy base
            # the HallucinatedPhoenixScout() is modified to scout more enemy tech line
        )

    def pvp_micro_build(self) -> BuildOrder:
        return BuildOrder(
            # TODO
            # keep optimize
            AutoWorker(),
            AutoPylon(),

            Step(Time(time_in_seconds=4 * 60),
                 Scout(UnitTypeId.PROBE, 1,
                       ScoutLocation.scout_enemy3(),
                       ScoutLocation.scout_enemy4(),
                       ScoutLocation.scout_enemy5(),
                       )
                 ),

            Step(Time(time_in_seconds=4 * 60),
                 Scout(UnitTypeId.PROBE, 1,
                       ScoutLocation.scout_enemy6(),
                       ScoutLocation.scout_enemy7(),
                       ScoutLocation.scout_enemy8(),
                       ),
                 ),

            ChronoAnyTech(save_to_energy=50),
            ChronoUnit(UnitTypeId.IMMORTAL, UnitTypeId.ROBOTICSFACILITY, 5),
            ChronoUnit(UnitTypeId.CARRIER, UnitTypeId.STARGATE, 5),
            ChronoUnit(UnitTypeId.MOTHERSHIP, UnitTypeId.NEXUS, 2),

            Step(Supply(90),
                 GridBuilding(unit_type=UnitTypeId.STARGATE, to_count=1, priority=True)),

            Tech(UpgradeId.BLINKTECH),

            [
                Tech(UpgradeId.PROTOSSGROUNDARMORSLEVEL1),
                Tech(UpgradeId.PROTOSSGROUNDWEAPONSLEVEL1),
                Tech(UpgradeId.PROTOSSSHIELDSLEVEL1),
            ],
            [
                Tech(UpgradeId.PROTOSSGROUNDARMORSLEVEL2),
                Tech(UpgradeId.PROTOSSGROUNDWEAPONSLEVEL2),
                Tech(UpgradeId.PROTOSSSHIELDSLEVEL2),
            ],

            # eco plan
            Step(UnitExists(UnitTypeId.NEXUS, 2), DefensiveCannons(0, 1, 1)),
            StepBuildGas(to_count=4, requirement=UnitExists(UnitTypeId.PROBE, 36)),
            StepBuildGas(to_count=6, requirement=UnitExists(UnitTypeId.NEXUS, 3)),

            Step(UnitExists(UnitTypeId.NEXUS, 2), GridBuilding(unit_type=UnitTypeId.ROBOTICSFACILITY, to_count=1)),
            Step(UnitExists(UnitTypeId.NEXUS, 2), GridBuilding(unit_type=UnitTypeId.TWILIGHTCOUNCIL, to_count=1)),
            Step(UnitExists(UnitTypeId.TWILIGHTCOUNCIL),
                 GridBuilding(unit_type=UnitTypeId.GATEWAY, to_count=6)),
            Step(Supply(80),
                 GridBuilding(unit_type=UnitTypeId.FORGE, to_count=1, priority=True)),
            Step(Supply(100), Expand(3, priority=True)),
            Step(EnemyUnitExists(UnitTypeId.NEXUS, 4), Expand(3, priority=True)),

            Step(Supply(105),
                 GridBuilding(unit_type=UnitTypeId.FLEETBEACON, to_count=1)),
            Step(UnitExists(UnitTypeId.FLEETBEACON),
                 ProtossUnit(UnitTypeId.MOTHERSHIP, to_count=1, priority=True)),

            # this is the final golden armada
            Step(UnitExists(UnitTypeId.TEMPEST, 1),
                 GridBuilding(unit_type=UnitTypeId.STARGATE, to_count=3)),
            ProtossUnit(UnitTypeId.CARRIER, priority=True, to_count=2),
            ProtossUnit(UnitTypeId.TEMPEST, priority=True, to_count=2),

            Step(EnemyUnitExists(UnitTypeId.TEMPEST, 1),
                 ProtossUnit(UnitTypeId.STALKER, priority=True)),

            # units

            ProtossUnit(UnitTypeId.OBSERVER, to_count=1, priority=True),
            Step(UnitExists(UnitTypeId.IMMORTAL, 4), ProtossUnit(UnitTypeId.WARPPRISM, to_count=1, priority=True)),
            Step(EnemyUnitExists(UnitTypeId.IMMORTAL, 4), ProtossUnit(UnitTypeId.IMMORTAL, priority=True, to_count=8)),
            ProtossUnit(UnitTypeId.IMMORTAL, priority=True, to_count=4),
            ProtossUnit(UnitTypeId.STALKER, priority=True),
            ProtossUnit(UnitTypeId.SENTRY, to_count=2, priority=True),
            ProtossUnit(UnitTypeId.VOIDRAY),

        )

    def counter_CannonRush(self) -> BuildOrder:
        # as long as I detected the cannon rush,
        # bot will go 4bg stalker pressure
        # this is tested 2020-08-06 with 100% clear advantage wins
        return BuildOrder(
            AutoWorker(),
            AutoPylon(),
            Cancel2ndBase(),

            ChronoUnit(UnitTypeId.STALKER, UnitTypeId.GATEWAY, 10),
            ChronoUnit(UnitTypeId.IMMORTAL, UnitTypeId.GATEWAY, 10),
            ProtossUnit(UnitTypeId.SENTRY, priority=True, to_count=1),
            ProtossUnit(UnitTypeId.IMMORTAL, priority=True),
            ProtossUnit(UnitTypeId.STALKER, priority=True),
            Tech(UpgradeId.WARPGATERESEARCH),

            Step(UnitExists(UnitTypeId.CYBERNETICSCORE),
                 GridBuilding(unit_type=UnitTypeId.GATEWAY, to_count=2, priority=True)),
            Step(UnitExists(UnitTypeId.CYBERNETICSCORE),
                 GridBuilding(unit_type=UnitTypeId.ROBOTICSFACILITY, to_count=1, priority=True)),
            GridBuilding(unit_type=UnitTypeId.CYBERNETICSCORE, to_count=1, priority=True),
        )

    def counter_ProxyZealots(self) -> BuildOrder:
        # as long as I detected the proxy zealot by getting no gas in enemy base,
        # bot will go 4bg stalker pressure
        # this is tested 2020-08-06 with 100% clear advantage wins
        # gotta say stalker micro is too OP!
        return BuildOrder(
            AutoWorker(),
            AutoPylon(),
            Cancel2ndBase(),

            ChronoUnit(UnitTypeId.STALKER, UnitTypeId.GATEWAY, 10),

            Tech(UpgradeId.WARPGATERESEARCH),
            Step(UnitExists(UnitTypeId.STALKER, 5),
                 GridBuilding(unit_type=UnitTypeId.GATEWAY, to_count=4, priority=True)),
            Step(UnitExists(UnitTypeId.CYBERNETICSCORE),
                 GridBuilding(unit_type=UnitTypeId.GATEWAY, to_count=3, priority=True)),
            ProtossUnit(UnitTypeId.STALKER, priority=True),
            GridBuilding(unit_type=UnitTypeId.GATEWAY, to_count=1, priority=True),
            GridBuilding(unit_type=UnitTypeId.CYBERNETICSCORE, to_count=1, priority=True),
            BuildGas(2),
        )

    def counter_4BG(self) -> BuildOrder:
        # 4BG = adept rush/stalker rush/ zealot rush
        # general eco strategy to counter 4 BG rush
        return BuildOrder(
            AutoWorker(),
            AutoPylon(),
            Cancel2ndBase(),

            ChronoUnit(UnitTypeId.IMMORTAL, UnitTypeId.ROBOTICSFACILITY, 10),

            GridBuilding(unit_type=UnitTypeId.GATEWAY, to_count=2, priority=True),
            GridBuilding(unit_type=UnitTypeId.CYBERNETICSCORE, to_count=1, priority=True),
            BuildGas(2),
            GridBuilding(unit_type=UnitTypeId.ROBOTICSFACILITY, to_count=1, priority=True),
            ProtossUnit(UnitTypeId.STALKER, to_count=3, priority=True),
            Tech(UpgradeId.WARPGATERESEARCH),
            Step(UnitExists(UnitTypeId.IMMORTAL), Expand(2, priority=True)),
            DefensiveCannons(0, 1, 1),
            Step(UnitExists(UnitTypeId.PROBE, 36),
                 BuildGas(4)),
            Step(UnitExists(UnitTypeId.NEXUS, 2),
                 GridBuilding(unit_type=UnitTypeId.GATEWAY, to_count=6, priority=True)),

            Step(EnemyUnitExists(UnitTypeId.VOIDRAY),
                 ProtossUnit(UnitTypeId.STALKER, priority=True, to_count=16)),
            Step(EnemyUnitExists(UnitTypeId.IMMORTAL),
                 ProtossUnit(UnitTypeId.IMMORTAL, priority=True, to_count=5)),
            Step(EnemyUnitExists(UnitTypeId.STALKER, 6),
                 ProtossUnit(UnitTypeId.IMMORTAL, priority=True, to_count=5)),

            ProtossUnit(UnitTypeId.OBSERVER, priority=True, to_count=1),
            ProtossUnit(UnitTypeId.STALKER, priority=True),
            ProtossUnit(UnitTypeId.SENTRY, to_count=1, priority=True),
            ProtossUnit(UnitTypeId.IMMORTAL, to_count=2, priority=True),
            StepBuildGas(requirement=UnitExists(UnitTypeId.PROBE, 36), to_count=4),
        )

    def counter_air(self) -> BuildOrder:
        return BuildOrder(
            AutoPylon(),
            AutoWorker(),

            GridBuilding(unit_type=UnitTypeId.GATEWAY, to_count=4, priority=True),
            Step(EnemyUnitExists(UnitTypeId.NEXUS, 2), Expand(2, priority=True)),
            DefensiveCannons(0, 1, 0),
            Step(Time(time_in_seconds=4 * 60),
                 Scout(UnitTypeId.PROBE, 1,
                       ScoutLocation.scout_enemy2(),
                       ScoutLocation.scout_enemy3(),
                       ScoutLocation.scout_enemy4(),
                       )
                 ),
            # chrono
            ChronoAnyTech(save_to_energy=50),
            ChronoUnit(UnitTypeId.STALKER, UnitTypeId.GATEWAY, 1),

            Tech(UpgradeId.WARPGATERESEARCH),
            Tech(UpgradeId.BLINKTECH),
            Step(UnitExists(UnitTypeId.NEXUS, 2),
                 GridBuilding(unit_type=UnitTypeId.ROBOTICSFACILITY, to_count=1, priority=True)),
            StepBuildGas(4, UnitExists(UnitTypeId.GATEWAY, 4)),
            Step(UnitExists(UnitTypeId.GATEWAY, 4),
                 GridBuilding(unit_type=UnitTypeId.TWILIGHTCOUNCIL, to_count=1, priority=True)),
            Step(UnitExists(UnitTypeId.NEXUS, 2),
                 GridBuilding(unit_type=UnitTypeId.GATEWAY, to_count=8, priority=True)),
            StepBuildGas(4, UnitExists(UnitTypeId.GATEWAY, 4)),

            # units

            Step(EnemyUnitExists(UnitTypeId.VOIDRAY),
                 ProtossUnit(UnitTypeId.STALKER, priority=True, to_count=8)),

            ProtossUnit(UnitTypeId.ADEPT, priority=True, to_count=2, only_once=True),
            ProtossUnit(UnitTypeId.SENTRY, priority=True, to_count=1, only_once=True),
            ProtossUnit(UnitTypeId.OBSERVER, priority=True, to_count=1),
            ProtossUnit(UnitTypeId.IMMORTAL, priority=True, to_count=5),
            ProtossUnit(UnitTypeId.STALKER, priority=True),
        )

    def counter_Robo_old(self) -> BuildOrder:
        # the only way to defeat early robo rush is to robo yourself!
        # and use the advantage of defense
        # this blink immortal is very OP and takes the advantage of
        # enemy not having air units
        return BuildOrder(
            AutoWorker(),
            AutoPylon(),
            Cancel2ndBase(),

            ChronoUnit(UnitTypeId.IMMORTAL, UnitTypeId.ROBOTICSFACILITY, 10),
            ChronoUnit(UnitTypeId.STALKER, UnitTypeId.GATEWAY, 10),
            ChronoUnit(UnitTypeId.WARPPRISM, UnitTypeId.ROBOTICSFACILITY, 1),

            GridBuilding(unit_type=UnitTypeId.GATEWAY, to_count=2, priority=True),
            GridBuilding(unit_type=UnitTypeId.CYBERNETICSCORE, to_count=1, priority=True),
            BuildGas(2),
            DefensiveCannons(0, 1, 0),
            Step(Supply(60),
                 Expand(2, priority=True)),
            StepBuildGas(requirement=UnitExists(UnitTypeId.PROBE, 36), to_count=4),

            Step(EnemyUnitExists(UnitTypeId.VOIDRAY),
                 ProtossUnit(UnitTypeId.STALKER, priority=True, to_count=8)),

            GridBuilding(unit_type=UnitTypeId.ROBOTICSFACILITY, to_count=2),

            Step(UnitExists(UnitTypeId.IMMORTAL, 4),
                 ProtossUnit(UnitTypeId.WARPPRISM, priority=True, to_count=1)),
            Step(UnitExists(UnitTypeId.IMMORTAL, 4),
                 ProtossUnit(UnitTypeId.OBSERVER, priority=True, to_count=1)),
            Step(UnitExists(UnitTypeId.IMMORTAL, 4),
                 ProtossUnit(UnitTypeId.STALKER, priority=True)),

            ProtossUnit(UnitTypeId.IMMORTAL, priority=True, to_count=4),
            ProtossUnit(UnitTypeId.SENTRY, to_count=2, priority=True),
            ProtossUnit(UnitTypeId.IMMORTAL, priority=True),
        )

    def counter_Robo(self) -> BuildOrder:
        return BuildOrder(
            AutoWorker(),
            AutoPylon(),
            Cancel2ndBase(),

            ChronoUnit(UnitTypeId.ORACLE, UnitTypeId.STARGATE, 1),
            ChronoUnit(UnitTypeId.VOIDRAY, UnitTypeId.STARGATE, 10),
            ChronoUnit(UnitTypeId.STALKER, UnitTypeId.GATEWAY, 10),

            GridBuilding(unit_type=UnitTypeId.GATEWAY, to_count=2, priority=True),
            GridBuilding(unit_type=UnitTypeId.CYBERNETICSCORE, to_count=1, priority=True),
            BuildGas(2),
            DefensiveCannons(0, 1, 0),
            Step(Supply(54),
                 Expand(2, priority=True)),
            StepBuildGas(requirement=UnitExists(UnitTypeId.PROBE, 36), to_count=4),

            Step(EnemyUnitExists(UnitTypeId.VOIDRAY),
                 ProtossUnit(UnitTypeId.STALKER, priority=True, to_count=8)),

            GridBuilding(unit_type=UnitTypeId.STARGATE, to_count=1),

            ProtossUnit(UnitTypeId.ORACLE, priority=True, to_count=1, only_once=True),
            Step(UnitExists(UnitTypeId.ORACLE, include_killed=True), ProtossUnit(UnitTypeId.VOIDRAY, priority=True)),
            ProtossUnit(UnitTypeId.STALKER, priority=True),
        )

    # TODO
    # not actually working well, go to micro
    def counter_EarlyExpand(self) -> BuildOrder:
        return BuildOrder(
            AutoWorker(),
            AutoPylon(),

            ChronoAnyTech(save_to_energy=50),
            ChronoUnit(UnitTypeId.IMMORTAL, UnitTypeId.ROBOTICSFACILITY, 10),

            GridBuilding(unit_type=UnitTypeId.GATEWAY, to_count=1, priority=True),
            GridBuilding(unit_type=UnitTypeId.CYBERNETICSCORE, to_count=1, priority=True),
            GridBuilding(unit_type=UnitTypeId.GATEWAY, to_count=4, priority=True),
            Tech(UpgradeId.WARPGATERESEARCH),

            ProtossUnit(UnitTypeId.ADEPT, priority=True, to_count=2, only_once=True),
            ProtossUnit(UnitTypeId.STALKER, priority=True)
        )

    def counter_FastDT(self) -> BuildOrder:
        return BuildOrder(
            AutoWorker(),
            AutoPylon(),

            ChronoUnit(UnitTypeId.OBSERVER, UnitTypeId.ROBOTICSFACILITY, 1),
            GridBuilding(unit_type=UnitTypeId.GATEWAY, to_count=1, priority=True),
            GridBuilding(unit_type=UnitTypeId.CYBERNETICSCORE, to_count=1, priority=True),
            GridBuilding(unit_type=UnitTypeId.ROBOTICSFACILITY, to_count=1, priority=True),
            ProtossUnit(UnitTypeId.OBSERVER, priority=True, to_count=1),

            ChronoUnit(UnitTypeId.IMMORTAL, UnitTypeId.ROBOTICSFACILITY, 3),

            GridBuilding(unit_type=UnitTypeId.GATEWAY, to_count=2, priority=True),
            ProtossUnit(UnitTypeId.STALKER, to_count=3, priority=True),
            Tech(UpgradeId.WARPGATERESEARCH),
            Expand(2),
            DefensiveCannons(0, 1, 1),

            Step(UnitExists(UnitTypeId.IMMORTAL, 2),
                 ProtossUnit(UnitTypeId.WARPPRISM, priority=True, to_count=1)),
            ProtossUnit(UnitTypeId.IMMORTAL, priority=True, to_count=3),

            ProtossUnit(UnitTypeId.SENTRY, to_count=2, priority=True),
            ProtossUnit(UnitTypeId.STALKER),

            StepBuildGas(requirement=UnitExists(UnitTypeId.PROBE, 36), to_count=4),
            Step(UnitExists(UnitTypeId.STALKER, 8),
                 GridBuilding(unit_type=UnitTypeId.GATEWAY, to_count=4, priority=True)),
            Step(UnitExists(UnitTypeId.PROBE, 38),
                 GridBuilding(unit_type=UnitTypeId.GATEWAY, to_count=7)),
        )

    # TODO: these are pvz related functions

    def pvz_main_force(self) -> BuildOrder:
        return BuildOrder(
            Step(lambda k: k.build_detector.rush_build == EnemyRushBuild.Macro, self.pvz_eco_start_up()),
            Step(lambda k: k.build_detector.rush_build == EnemyRushBuild.EcoExpand, self.pvz_micro_build()),
            Step(lambda k: k.build_detector.rush_build == EnemyRushBuild.LingRush, self.couter_ling_rush()),

            Step(lambda k: k.build_detector.rush_build == EnemyRushBuild.RoachRush, self.couter_roach_rush()),
            # Step(lambda k: k.build_detector.rush_build == EnemyRushBuild.NySwarm, self.couter_nyd_rush()),
            Step(lambda k: k.build_detector.rush_build == EnemyRushBuild.NySwarm, self.pvz_micro_build()),
            Step(lambda k: k.build_detector.rush_build == EnemyRushBuild.WorkerRush, self.pvz_micro_build()),
        )

    def pvz_eco_start_up(self) -> SequentialList:
        return SequentialList(
            Workers(13),
            GridBuilding(unit_type=UnitTypeId.PYLON, to_count=1, priority=True),
            Workers(14),

            GridBuilding(unit_type=UnitTypeId.GATEWAY, to_count=1, priority=True),
            WorkerScout(),
            Workers(16),
            Expand(2, priority=True),
            GridBuilding(unit_type=UnitTypeId.CYBERNETICSCORE, to_count=1, priority=True),
            # should have seen enemy 2nd base at ~ 1:12
            # either 2 base eco or 1 base rushes
        )

    def couter_roach_rush(self) -> BuildOrder:
        return BuildOrder(
            ChronoAnyTech(save_to_energy=50),
            Cancel2ndBase(),
            DefensiveCannons(0, 1, 1),

            AutoPylon(),
            AutoWorker(),

            GridBuilding(unit_type=UnitTypeId.CYBERNETICSCORE, to_count=1, priority=True),
            GridBuilding(unit_type=UnitTypeId.PYLON, to_count=2, priority=True),
            BuildGas(2),
            ProtossUnit(UnitTypeId.ZEALOT, to_count=1, priority=True, only_once=True),
            GridBuilding(unit_type=UnitTypeId.GATEWAY, to_count=2, priority=True),
            ProtossUnit(UnitTypeId.STALKER, to_count=2, priority=True),
            Tech(UpgradeId.WARPGATERESEARCH),
            GridBuilding(unit_type=UnitTypeId.GATEWAY, to_count=4, priority=True),
            ProtossUnit(UnitTypeId.STALKER, to_count=8, priority=True),
            Step(Supply(44),
                 GridBuilding(unit_type=UnitTypeId.GATEWAY, to_count=8, priority=True)),
            StepBuildGas(4, UnitExists(UnitTypeId.GATEWAY, 6)),

            Step(EnemyUnitExists(UnitTypeId.ZERGLING, 8),
                 ProtossUnit(UnitTypeId.ADEPT, priority=True, to_count=14)),

            ProtossUnit(UnitTypeId.ADEPT, priority=True, to_count=3, only_once=True),
            ProtossUnit(UnitTypeId.STALKER, priority=True),
        )

    def couter_ling_rush(self) -> BuildOrder:
        return BuildOrder(
            ChronoAnyTech(save_to_energy=50),
            Cancel2ndBase(),
            DefensiveCannons(0, 1, 1),

            AutoPylon(),
            AutoWorker(),

            GridBuilding(unit_type=UnitTypeId.CYBERNETICSCORE, to_count=1, priority=True),
            GridBuilding(unit_type=UnitTypeId.PYLON, to_count=2, priority=True),
            BuildGas(2),
            ProtossUnit(UnitTypeId.ZEALOT, to_count=1, priority=True, only_once=True),
            GridBuilding(unit_type=UnitTypeId.GATEWAY, to_count=2, priority=True),
            ProtossUnit(UnitTypeId.ADEPT, to_count=2, priority=True),
            Tech(UpgradeId.WARPGATERESEARCH),
            GridBuilding(unit_type=UnitTypeId.GATEWAY, to_count=4, priority=True),
            ProtossUnit(UnitTypeId.ADEPT, to_count=8, priority=True),
            Step(Supply(44),
                 Expand(2, priority=True)),
            Step(UnitExists(UnitTypeId.NEXUS, 2),
                 GridBuilding(unit_type=UnitTypeId.GATEWAY, to_count=8, priority=True)),
            StepBuildGas(4, UnitExists(UnitTypeId.GATEWAY, 6)),

            Step(EnemyUnitExists(UnitTypeId.ZERGLING, 8),
                 ProtossUnit(UnitTypeId.ADEPT, priority=True, to_count=14)),

            ProtossUnit(UnitTypeId.ADEPT, priority=True, to_count=3, only_once=True),
            ProtossUnit(UnitTypeId.STALKER, priority=True),
        )

    def couter_nyd_rush(self) -> BuildOrder:
        return BuildOrder(
            ChronoAnyTech(save_to_energy=0),
            ChronoUnit(UnitTypeId.ZEALOT, UnitTypeId.GATEWAY, 3),
            ChronoUnit(UnitTypeId.STALKER, UnitTypeId.GATEWAY, 8),

            Cancel2ndBase(),
            BuildGas(2),
            Step(UnitExists(UnitTypeId.STALKER, 8),
                 Expand(2, priority=True)),
            AutoPylon(),
            AutoWorker(),

            GridBuilding(unit_type=UnitTypeId.CYBERNETICSCORE, to_count=1, priority=True),
            GridBuilding(unit_type=UnitTypeId.PYLON, to_count=2, priority=True),
            GridBuilding(unit_type=UnitTypeId.GATEWAY, to_count=2, priority=True),
            ProtossUnit(UnitTypeId.STALKER, to_count=2, priority=True),
            GridBuilding(unit_type=UnitTypeId.GATEWAY, to_count=3, priority=True),
            ProtossUnit(UnitTypeId.STALKER, to_count=8, priority=True),
            Tech(UpgradeId.WARPGATERESEARCH),
            Step(Supply(44),
                 GridBuilding(unit_type=UnitTypeId.GATEWAY, to_count=8, priority=True)),
            StepBuildGas(4, UnitExists(UnitTypeId.GATEWAY, 6)),

            Step(EnemyUnitExists(UnitTypeId.ZERGLING, 8),
                 ProtossUnit(UnitTypeId.ADEPT, priority=True, to_count=14)),

            ProtossUnit(UnitTypeId.ADEPT, priority=True, to_count=3, only_once=True),
            ProtossUnit(UnitTypeId.STALKER, priority=True),
        )

    def pvz_micro_build(self) -> BuildOrder:
        # when enemy goes for 2nd base
        return BuildOrder(

            AutoPylon(),
            AutoWorker(),

            GridBuilding(unit_type=UnitTypeId.CYBERNETICSCORE, to_count=1, priority=True),
            GridBuilding(unit_type=UnitTypeId.PYLON, to_count=2, priority=True),
            ProtossUnit(UnitTypeId.ZEALOT, to_count=1, priority=True),
            GridBuilding(unit_type=UnitTypeId.GATEWAY, to_count=2, priority=True),
            BuildGas(2),
            Step(EnemyUnitExists(UnitTypeId.ZERGLING, 2),
                 ProtossUnit(UnitTypeId.ADEPT, priority=True, to_count=4)),
            ProtossUnit(UnitTypeId.SENTRY, to_count=2, priority=True),
            GridBuilding(unit_type=UnitTypeId.GATEWAY, to_count=4, priority=True),

            ProtossUnit(UnitTypeId.ADEPT, to_count=4, priority=True, only_once=True),
            Tech(UpgradeId.WARPGATERESEARCH),

            Step(UnitExists(UnitTypeId.HIGHTEMPLAR, 4), Archon([UnitTypeId.HIGHTEMPLAR])),
            Step(UnitExists(UnitTypeId.GATEWAY, 7),
                 GridBuilding(unit_type=UnitTypeId.ROBOTICSFACILITY, to_count=1, priority=True)),
            Step(UnitExists(UnitTypeId.GATEWAY, 7),
                 GridBuilding(unit_type=UnitTypeId.TWILIGHTCOUNCIL, to_count=1, priority=True)),
            Step(UnitExists(UnitTypeId.TWILIGHTCOUNCIL),
                 GridBuilding(unit_type=UnitTypeId.TEMPLARARCHIVE, to_count=1, priority=True)),

            Step(Time(time_in_seconds=3 * 60),
                 Scout(UnitTypeId.PROBE, 1,
                       ScoutLocation.scout_enemy3(),
                       ScoutLocation.scout_enemy4(),
                       ScoutLocation.scout_enemy5(),
                       )
                 ),

            # chrono
            ChronoAnyTech(save_to_energy=50),
            ChronoUnit(UnitTypeId.ADEPT, UnitTypeId.GATEWAY, 8),
            ChronoUnit(UnitTypeId.STALKER, UnitTypeId.GATEWAY, 8),

            Tech(UpgradeId.PSISTORMTECH),

            Step(EnemyUnitExists(UnitTypeId.ROACH, 3),
                 ProtossUnit(UnitTypeId.IMMORTAL, priority=True, to_count=3)),
            Step(EnemyUnitExists(UnitTypeId.ROACH, 3),
                 ProtossUnit(UnitTypeId.STALKER, priority=True, to_count=8)),
            Step(EnemyUnitExists(UnitTypeId.ZERGLING, 8),
                 ProtossUnit(UnitTypeId.ADEPT, priority=True, to_count=14)),

            Step(Supply(44),
                 GridBuilding(unit_type=UnitTypeId.GATEWAY, to_count=8, priority=True)),
            StepBuildGas(4, UnitExists(UnitTypeId.GATEWAY, 6)),

            # units

            ProtossUnit(UnitTypeId.OBSERVER, priority=True, to_count=1),
            ProtossUnit(UnitTypeId.ADEPT, priority=True, to_count=8),
            ProtossUnit(UnitTypeId.HIGHTEMPLAR, priority=True, to_count=4),
            ProtossUnit(UnitTypeId.STALKER, priority=True),

        )

    # python run_custom.py -m OdysseyLE -p1 protossbot -p2 lingflood

    def pvt_main_force(self) -> BuildOrder:
        return BuildOrder(
            Step(lambda k: k.build_detector.rush_build == EnemyRushBuild.Macro, self.pvt_eco_start_up()),

            Step(lambda k: k.build_detector.rush_build == EnemyRushBuild.ProxyMarine, self.counter_marine()),
            Step(lambda k: k.build_detector.rush_build == EnemyRushBuild.ProxyMarauders, self.counter_marader()),
            Step(lambda k: k.build_detector.rush_build == EnemyRushBuild.ProxyFactory, self.pvt_micro()),
            Step(lambda k: k.build_detector.rush_build == EnemyRushBuild.TerranMacro, self.pvt_micro()),
            Step(lambda k: k.build_detector.rush_build == EnemyRushBuild.WorkerRush, self.pvt_micro()),

        )

    def pvt_micro(self) -> BuildOrder:
        return BuildOrder(
            self.pvt_micro_build()
        )

    def pvt_eco_start_up(self) -> SequentialList:
        return SequentialList(
            Workers(13),
            GridBuilding(unit_type=UnitTypeId.PYLON, to_count=1, priority=True),
            Workers(14),
            GridBuilding(unit_type=UnitTypeId.GATEWAY, to_count=1, priority=True),
            # worker scout time that can not be blocked
            WorkerScout(),
            # 0:40 enemy open worker rush build
            Step(UnitExists(UnitTypeId.NEXUS), action=ChronoUnit(UnitTypeId.PROBE, UnitTypeId.NEXUS, 1)),
            Workers(16),
            BuildGas(1),
            Workers(18),
            GridBuilding(unit_type=UnitTypeId.CYBERNETICSCORE, to_count=1, priority=True),
        )

    def pvt_micro_build(self) -> BuildOrder:
        return BuildOrder(
            AutoWorker(),
            AutoPylon(),

            Step(Time(time_in_seconds=4 * 60),
                 Scout(UnitTypeId.PROBE, 1,
                       ScoutLocation.scout_enemy3(),
                       ScoutLocation.scout_enemy4(),
                       ScoutLocation.scout_enemy5(),
                       )
                 ),

            Step(Time(time_in_seconds=5 * 60),
                 Scout(UnitTypeId.PROBE, 1,
                       ScoutLocation.scout_enemy6(),
                       ScoutLocation.scout_enemy7(),
                       ScoutLocation.scout_enemy8(),
                       ),
                 ),

            ChronoAnyTech(save_to_energy=50),
            ChronoUnit(UnitTypeId.ORACLE, UnitTypeId.STARGATE, 1),
            ChronoUnit(UnitTypeId.IMMORTAL, UnitTypeId.ROBOTICSFACILITY),

            Expand(2, priority=True),
            BuildGas(2),
            GridBuilding(unit_type=UnitTypeId.GATEWAY, to_count=4, priority=True),

            # TODO eco
            Step(UnitExists(UnitTypeId.GATEWAY, 4),
                 GridBuilding(unit_type=UnitTypeId.TWILIGHTCOUNCIL, to_count=1, priority=True)),
            Step(Supply(100),
                 GridBuilding(unit_type=UnitTypeId.FORGE, to_count=1, priority=True)),
            Step(Gas(400),
                 GridBuilding(unit_type=UnitTypeId.TEMPLARARCHIVE, to_count=1, priority=True)),
            Step(Time(time_in_seconds=6 * 60), DefensiveCannons(0, 1)),
            Step(UnitExists(UnitTypeId.NEXUS, 2),
                 GridBuilding(unit_type=UnitTypeId.ROBOTICSFACILITY, to_count=1, priority=True)),
            Step(UnitExists(UnitTypeId.NEXUS, 2),
                 GridBuilding(unit_type=UnitTypeId.GATEWAY, to_count=8, priority=True)),
            Step(UnitExists(UnitTypeId.NEXUS, 4),
                 GridBuilding(unit_type=UnitTypeId.FLEETBEACON, to_count=1, priority=True)),
            Step(UnitExists(UnitTypeId.NEXUS, 4),
                 GridBuilding(unit_type=UnitTypeId.STARGATE, to_count=3, priority=True)),
            StepBuildGas(requirement=UnitExists(UnitTypeId.PROBE, 34), to_count=4),
            Step(Supply(76),
                 Expand(3, priority=True)),
            Step(UnitExists(UnitTypeId.PROBE, 56),
                 GridBuilding(unit_type=UnitTypeId.GATEWAY, to_count=14, priority=True)),
            StepBuildGas(4, UnitExists(UnitTypeId.NEXUS, 2)),
            StepBuildGas(6, UnitExists(UnitTypeId.NEXUS, 3)),

            # TODO tech
            Tech(UpgradeId.WARPGATERESEARCH),
            ProtossUnit(UnitTypeId.ADEPT, priority=True, to_count=1, only_once=True),
            Step(EnemyUnitExists(UnitTypeId.REAPER, 1),
                 ProtossUnit(UnitTypeId.ADEPT, priority=True, to_count=2, only_once=True)),
            Step(EnemyUnitExists(UnitTypeId.REAPER, 2),
                 ProtossUnit(UnitTypeId.ADEPT, priority=True, to_count=4, only_once=True)),
            Tech(UpgradeId.CHARGE),
            Tech(UpgradeId.PSISTORMTECH),
            [
                Tech(UpgradeId.PROTOSSGROUNDARMORSLEVEL1),
                Tech(UpgradeId.PROTOSSGROUNDWEAPONSLEVEL1),
                Tech(UpgradeId.PROTOSSSHIELDSLEVEL1),
            ],
            [
                Tech(UpgradeId.PROTOSSGROUNDARMORSLEVEL2),
                Tech(UpgradeId.PROTOSSGROUNDWEAPONSLEVEL2),
                Tech(UpgradeId.PROTOSSSHIELDSLEVEL2),
            ],
            Step(UnitExists(UnitTypeId.STALKER, 6),
                 Tech(UpgradeId.BLINKTECH)),

            # TODO couter attack
            ProtossUnit(UnitTypeId.HIGHTEMPLAR, priority=True, to_count=2),
            Step(UnitExists(UnitTypeId.HIGHTEMPLAR, 5), Archon([UnitTypeId.HIGHTEMPLAR])),
            Step(EnemyUnitExists(UnitTypeId.BATTLECRUISER, 1),
                 ProtossUnit(UnitTypeId.STALKER, priority=True, to_count=10)),
            Step(EnemyUnitExists(UnitTypeId.BANSHEE, 1),
                 ProtossUnit(UnitTypeId.STALKER, priority=True, to_count=10)),
            Step(EnemyUnitExists(UnitTypeId.MARAUDER, 4),
                 ProtossUnit(UnitTypeId.IMMORTAL, priority=True, to_count=2)),
            Step(EnemyUnitExists(UnitTypeId.MARINE, 4),
                 ProtossUnit(UnitTypeId.ADEPT, priority=True, to_count=6)),

            # TODO unit
            Step(UnitExists(UnitTypeId.FLEETBEACON),
                 ProtossUnit(UnitTypeId.MOTHERSHIP, priority=True, to_count=1)),
            Step(UnitExists(UnitTypeId.FLEETBEACON),
                 ProtossUnit(UnitTypeId.CARRIER, priority=True, to_count=3)),
            Step(UnitExists(UnitTypeId.FLEETBEACON),
                 ProtossUnit(UnitTypeId.TEMPEST, priority=True)),

            ProtossUnit(UnitTypeId.SENTRY, priority=True, to_count=1, only_once=True),
            ProtossUnit(UnitTypeId.OBSERVER, priority=True, to_count=1),
            ProtossUnit(UnitTypeId.WARPPRISM, priority=True, to_count=1),
            Step(EnemyUnitExists(UnitTypeId.SIEGETANKSIEGED, 1),
                 ProtossUnit(UnitTypeId.ZEALOT, priority=True, to_count=15)),
            Step(Minerals(1100),
                 ProtossUnit(UnitTypeId.ZEALOT, priority=True)),
            Step(Gas(800),
                 ProtossUnit(UnitTypeId.HIGHTEMPLAR, priority=True)),
            ProtossUnit(UnitTypeId.HIGHTEMPLAR, priority=True, to_count=4),
            ProtossUnit(UnitTypeId.STALKER, priority=True),
        )

    def counter_marine(self) -> BuildOrder:
        return BuildOrder(
            Cancel2ndBase(),
            ChronoAnyTech(save_to_energy=50),

            Tech(UpgradeId.WARPGATERESEARCH),

            BuildGas(2),

            GridBuilding(unit_type=UnitTypeId.GATEWAY, to_count=3, priority=True),
            GridBuilding(unit_type=UnitTypeId.CYBERNETICSCORE, to_count=1, priority=True),
            Step(Supply(38),
                 GridBuilding(unit_type=UnitTypeId.STARGATE, to_count=1, priority=True)),

            ProtossUnit(UnitTypeId.ADEPT, priority=True, to_count=3, only_once=True),
            ProtossUnit(UnitTypeId.ADEPT, priority=True, to_count=8),
            ProtossUnit(UnitTypeId.ORACLE, priority=True, to_count=1, only_once=True),
            ProtossUnit(UnitTypeId.STALKER, priority=True),

            AutoWorker(),
            AutoPylon(),
        )

    def counter_marader(self) -> BuildOrder:
        return BuildOrder(

            AutoPylon(),
            AutoWorker(),

            Cancel2ndBase(),
            BuildGas(2),
            ChronoAnyTech(save_to_energy=50),
            ChronoUnit(UnitTypeId.IMMORTAL, UnitTypeId.ROBOTICSFACILITY, 5),
            GridBuilding(unit_type=UnitTypeId.GATEWAY, to_count=2, priority=True),
            GridBuilding(unit_type=UnitTypeId.CYBERNETICSCORE, to_count=1, priority=True),
            GridBuilding(unit_type=UnitTypeId.ROBOTICSFACILITY, to_count=1, priority=True),
            DefensiveCannons(0, 1, 0),
            ProtossUnit(UnitTypeId.SENTRY, to_count=1, priority=True, only_once=True),
            ProtossUnit(UnitTypeId.STALKER, to_count=1, priority=True, only_once=True),
            Tech(UpgradeId.WARPGATERESEARCH),

            Step(EnemyUnitExists(UnitTypeId.BANSHEE),
                 ProtossUnit(UnitTypeId.STALKER, priority=True)),

            Step(UnitExists(UnitTypeId.IMMORTAL, 2),
                 GridBuilding(unit_type=UnitTypeId.STARGATE, to_count=1, priority=True)),
            ProtossUnit(UnitTypeId.ORACLE, priority=True, to_count=1, only_once=True),
            ProtossUnit(UnitTypeId.IMMORTAL, priority=True),
            ProtossUnit(UnitTypeId.STALKER, priority=True)
        )

    # python run_custom.py -m EverDreamLE -p1 protossbot -p2 200roach

    def pvr_main_force(self) -> BuildOrder:
        return BuildOrder(
            Step(lambda k: k.build_detector.rush_build == EnemyRushBuild.Macro, self.pvp_eco_start_up()),

            # todo pvz
            Step(lambda k: k.build_detector.rush_build == EnemyRushBuild.EcoExpand, self.pvz_micro_build()),
            Step(lambda k: k.build_detector.rush_build == EnemyRushBuild.LingRush, self.pvz_micro_build()),

            Step(lambda k: k.build_detector.rush_build == EnemyRushBuild.RoachRush, self.couter_roach_rush()),
            Step(lambda k: k.build_detector.rush_build == EnemyRushBuild.NySwarm, self.couter_nyd_rush()),

            # todo pvp
            Step(lambda k: k.build_detector.rush_build == EnemyRushBuild.SafeExpand, self.pvp_micro()),

            Step(lambda k: k.build_detector.rush_build == EnemyRushBuild.WorkerRush, self.counter_ProxyZealots()),
            Step(lambda k: k.build_detector.rush_build == EnemyRushBuild.ProxyZealots, self.counter_ProxyZealots()),

            Step(lambda k: k.build_detector.rush_build == EnemyRushBuild.CannonRush, self.counter_CannonRush()),

            Step(lambda k: k.build_detector.rush_build == EnemyRushBuild.ProxyBase, self.counter_4BG()),
            Step(lambda k: k.build_detector.rush_build == EnemyRushBuild.Zealots, self.counter_4BG()),
            Step(lambda k: k.build_detector.rush_build == EnemyRushBuild.AdeptRush, self.counter_4BG()),

            Step(lambda k: k.build_detector.rush_build == EnemyRushBuild.AirOneBase, self.counter_air()),

            Step(lambda k: k.build_detector.rush_build == EnemyRushBuild.ProxyRobo, self.counter_Robo()),
            Step(lambda k: k.build_detector.rush_build == EnemyRushBuild.RoboRush, self.counter_Robo()),

            Step(lambda k: k.build_detector.rush_build == EnemyRushBuild.EarlyExpand, self.counter_EarlyExpand()),

            Step(lambda k: k.build_detector.rush_build == EnemyRushBuild.FastDT, self.counter_FastDT()),

            # todo pvt
            Step(lambda k: k.build_detector.rush_build == EnemyRushBuild.ProxyMarine, self.counter_marine()),
            Step(lambda k: k.build_detector.rush_build == EnemyRushBuild.ProxyMarauders, self.counter_marader()),
            Step(lambda k: k.build_detector.rush_build == EnemyRushBuild.ProxyFactory, self.pvt_micro()),
            Step(lambda k: k.build_detector.rush_build == EnemyRushBuild.TerranMacro, self.pvt_micro()),
            self.pvp_micro()
        )
