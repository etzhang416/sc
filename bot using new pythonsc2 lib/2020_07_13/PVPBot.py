
import sc2
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.ability_id import AbilityId
from sc2.ids.upgrade_id import UpgradeId
from sc2.ids.buff_id import BuffId
from sc2.unit import Unit
from sc2.units import Units
from sc2.position import Point2
from Pstrategy_id import ProtossFirstStageStrategyId, ProtossStartUpStrategyId


class PVPBot(sc2.BotAI):

    def __init__(self):
        # Initialize inherited class
        sc2.BotAI.__init__(self)


        # useful abstractions 
        self.ITERATIONS_PER_MINUTE = 165
        #base management
        self.first_nexus = None
        self.second_nexus = None
        self.third_nexus = None
        self.enemy_has_second_base = False
        self.enemy_second_base_location = None
        #strategies
        self.my_start_up_strategy = None
        self.my_technology_line_strategy = None
        self.enemy_start_up_strategy = ProtossStartUpStrategyId.UNKNOWNSTARTUPSTRATEGY
        self.enemy_technology_line_strategy = ProtossFirstStageStrategyId.UNKNOWNTECHLINE
        #oracle
        self.first_oracle_countered = False
        self.first_oracle = None
        self.oracle_flank_position = None
        self.oracle_reached_flank_position = False
        self.oracle_begin_attack_workers = False
        self.enemy_second_base_empty = True
        self.oracle_intel_gathered = False
        #scout
        self.first_scout_probe = None
        #force managment
        self.main_force = None







    def get_current_run_time_seconds(self):
        return int(self.time)
    
    async def on_step(self, iteration):

        await self.basic_attack_and_defend()


        if self.get_current_run_time_seconds() < 100:
            await self.two_BG_start_up()
        else:
            await self.start_up_evaluation()
            await self.quick_build_up_economy()
            await self.first_oracle_mission()

            await self.assign_nexuses()
            
            await self.zealot_charge_white_ball()
            # await self.quick_build_up_VS_tech()
            # await self.quick_build_up_VC_tech()




    #these functions are for specific start up strats

    # 1BG Nexus NY
    # at 100s, will have about 50 minerals and 50 gas
    async def eco_start_up(self):
        await self.assign_nexuses()
        await self.distribute_workers()
        if self.my_start_up_strategy == None:
            self.my_start_up_strategy = ProtossStartUpStrategyId.ECOSTARTUP
        if self.get_current_run_time_seconds() < 13:
            await self.build_one_probe()
        elif self.get_current_run_time_seconds() < 18:
            await self.build_first_pylon()
        elif self.get_current_run_time_seconds() < 38:
            await self.build_one_probe()
        elif self.get_current_run_time_seconds() < 40:
            await self.build_one_gateway()
        elif self.get_current_run_time_seconds() < 41:
            await self.first_chronoboost_probe_production()
        elif self.get_current_run_time_seconds() < 46:
            await self.build_first_assimilator()
        elif self.get_current_run_time_seconds() < 60:
            await self.build_one_probe()
        elif self.get_current_run_time_seconds() < 80:
            await self.build_one_probe()
            await self.send_first_probe_scout()
        elif self.get_current_run_time_seconds() < 90:
            await self.expand_second_nexus()
        elif self.get_current_run_time_seconds() < 99:
            await self.build_first_cyberneticscore()
        elif self.get_current_run_time_seconds() < 100:
            await self.build_second_assimilator()
        

    # 2BG start up 
    # at 100s, will have about 120 minerals and 36 gas
    async def two_BG_start_up(self):
        await self.assign_nexuses()
        await self.distribute_workers()
        if self.my_start_up_strategy == None:
            self.my_start_up_strategy = ProtossStartUpStrategyId.TWOBGSTARTUP
        if self.get_current_run_time_seconds() < 13:
            await self.build_one_probe()
        elif self.get_current_run_time_seconds() < 20:
            await self.build_first_pylon()
        elif self.get_current_run_time_seconds() < 29:
            await self.build_one_probe()
        elif self.get_current_run_time_seconds() < 39:
            await self.build_one_gateway()
        elif self.get_current_run_time_seconds() < 42:
            await self.build_one_probe()
            await self.first_chronoboost_probe_production()
        elif self.get_current_run_time_seconds() < 45:
            await self.build_first_assimilator()
        elif self.get_current_run_time_seconds() < 52:
            await self.build_one_probe()
        elif self.get_current_run_time_seconds() < 60:
            await self.build_second_assimilator()
        elif self.get_current_run_time_seconds() < 65:
            await self.build_one_probe()
            await self.send_first_probe_scout()
        elif self.get_current_run_time_seconds() < 68:
            await self.build_one_gateway()
        elif self.get_current_run_time_seconds() < 84:
            await self.build_one_probe()
        elif self.get_current_run_time_seconds() < 90:
            await self.build_first_cyberneticscore()
        elif self.get_current_run_time_seconds() < 93:
            await self.build_one_pylon()
        elif self.get_current_run_time_seconds() < 100:
            await self.build_one_probe()

    # These are functions for start up
    async def assign_nexuses(self):
        if self.enemy_second_base_location == None:
            self.enemy_second_base_location = await self.get_enemy_second_expansion_position()
            print("assigned enemy 2nd base location")
        if self.first_nexus == None:
             self.first_nexus = self.townhalls.ready.first
             print("assigned 1st base")
        if self.second_nexus == None:
            for nexus in self.townhalls:
                if nexus != self.first_nexus:
                    self.second_nexus = nexus
                    print("assigned 2nd base")
        if self.third_nexus == None:
            for nexus in self.townhalls.ready:
                if nexus != self.first_nexus and nexus != self.second_nexus:
                    self.third_nexus = nexus
                    print("assigned 3rd base")

    async def build_one_probe(self):
        nexus = self.townhalls.ready.first
        if self.can_afford(UnitTypeId.PROBE) and nexus.is_idle and \
           self.supply_left >= 1:
            nexus.train(UnitTypeId.PROBE)
            print("build one probe at")
            print(self.get_current_run_time_seconds())
        return

    async def build_first_pylon(self):
        nexus = self.first_nexus
        if self.already_pending(UnitTypeId.PYLON) == 0 \
           and self.can_afford(UnitTypeId.PYLON):
            await self.build(UnitTypeId.PYLON, near=nexus.position.towards(self.game_info.map_center, 7))
            print("build 1st pylon at")
            print(self.get_current_run_time_seconds())

    async def build_one_pylon(self):
        position = None
        for nexus in self.townhalls:
            nexus_has_pylon_around = False
            for pylon in self.structures(UnitTypeId.PYLON):
                if pylon.distance_to(nexus) <= 8:
                    nexus_has_pylon_around = True
                    break
            if not nexus_has_pylon_around:
                position = nexus.position.towards(self.game_info.map_center, 5)
        if position == None:
            position = self.townhalls.random.position.towards_with_random_angle(self.first_nexus.position,14)
        if self.can_afford(UnitTypeId.PYLON):
            await self.build(UnitTypeId.PYLON, position)
            print("build one pylon at")
            print(self.get_current_run_time_seconds())

    async def build_one_gateway(self):
        if self.can_afford(UnitTypeId.GATEWAY) and self.structures(UnitTypeId.PYLON).ready:
            pylon = self.structures(UnitTypeId.PYLON).ready.first
            await self.build(UnitTypeId.GATEWAY, near=pylon)
            print("build one gateway at")
            print(self.get_current_run_time_seconds())

    async def build_first_assimilator(self):
        nexus = self.townhalls.ready.first
        vg = self.vespene_geyser.closer_than(15, nexus).first
        if self.can_afford(UnitTypeId.ASSIMILATOR) and \
           not self.structures(UnitTypeId.ASSIMILATOR) and \
           self.already_pending(UnitTypeId.ASSIMILATOR) == 0 and \
           self.structures(UnitTypeId.NEXUS).ready.amount == 1:
            worker = self.select_build_worker(vg.position)
            worker.build(UnitTypeId.ASSIMILATOR, vg)
            worker.stop(queue=True)
            print("build 1st gas at")
            print(self.get_current_run_time_seconds())

    async def build_second_assimilator(self):
        nexus = self.townhalls.ready.first
        vgs = self.vespene_geyser.closer_than(15, nexus)
        for vg in vgs:
            if not self.gas_buildings.closer_than(1, vg) and \
               self.can_afford(UnitTypeId.ASSIMILATOR) and( \
               (self.already_pending(UnitTypeId.ASSIMILATOR) == 0 and \
               self.structures(UnitTypeId.NEXUS).ready.amount == 1) or ( \
               self.already_pending(UnitTypeId.ASSIMILATOR) == 1 and \
               self.structures(UnitTypeId.ASSIMILATOR).ready.amount == 0)):
                worker = self.select_build_worker(vg.position)
                worker.build(UnitTypeId.ASSIMILATOR, vg)
                worker.stop(queue=True)
                print("build 2nd gas at")
                print(self.get_current_run_time_seconds())

    async def expand_second_nexus(self):
        if self.can_afford(UnitTypeId.NEXUS) and self.second_nexus == None:
            await self.expand_now()
            print("build 2nd nexus at")
            print(self.get_current_run_time_seconds())
            
    async def build_first_cyberneticscore(self):
        if self.structures(UnitTypeId.GATEWAY).ready \
           and not self.structures(UnitTypeId.CYBERNETICSCORE) and \
           self.already_pending(UnitTypeId.CYBERNETICSCORE) == 0 and \
           self.can_afford(UnitTypeId.CYBERNETICSCORE):
            pylon = self.structures(UnitTypeId.PYLON).ready.first
            await self.build(UnitTypeId.CYBERNETICSCORE, near=pylon)
            print("build 1st cybernaticscore at")
            print(self.get_current_run_time_seconds())

    async def first_chronoboost_probe_production(self):
        nexus = self.structures(UnitTypeId.NEXUS).ready.first
        if (not nexus.has_buff(BuffId.CHRONOBOOSTENERGYCOST)) \
            and nexus.energy >= 50:
            nexus(AbilityId.EFFECT_CHRONOBOOSTENERGYCOST, nexus)
            print("first_chronoboost_probe_production at")
            print(self.get_current_run_time_seconds())





    # These are functions for intelligence gatering

    async def get_enemy_second_expansion_position(self):
        """Find enemy's 2nd expansion location."""
        closest = None
        known_smallest_distance = 99999
        startp = self.enemy_start_locations[0]

        for possible_location in self.expansion_locations_list:
            d = await self._client.query_pathing(startp, possible_location)
            if d is None:
                continue
            if d < known_smallest_distance and d >= 5:
                known_smallest_distance = d
                closest = possible_location

        return closest

    async def send_first_probe_scout(self):
        if self.first_scout_probe == None:
            self.first_scout_probe = self.units(UnitTypeId.PROBE).filter(lambda unit: not unit.is_carrying_resource).first
            print("send scout at")
            print(self.get_current_run_time_seconds())
        self.first_scout_probe.move(self.enemy_start_locations[0].towards(self.game_info.map_center, -3))
        return 



    # these functions are for researches
    # BY researches
    #test economy functions
    async def quick_build_up_VS_tech(self):
        await self.research_gateway_warpgate()
        await self.research_protossairweapon_level1()
        await self.research_protossairweapon_level2()
        await self.research_protossairweapon_level3()
        await self.research_protossairarmor_level1()
        await self.research_protossairarmor_level2()
        await self.research_protossairarmor_level3()

    async def research_gateway_warpgate(self):
        if self.structures(UnitTypeId.CYBERNETICSCORE).ready.exists and self.can_afford(AbilityId.RESEARCH_WARPGATE) \
            and self.already_pending_upgrade(UpgradeId.WARPGATERESEARCH) == 0:
            BY = self.structures(UnitTypeId.CYBERNETICSCORE).ready.first
            if BY.is_idle:
                BY.research(UpgradeId.WARPGATERESEARCH)
                print("research_gateway_warpgate at")
                print(self.get_current_run_time_seconds())

    async def research_protossairweapon_level1(self):
        if self.structures(UnitTypeId.CYBERNETICSCORE).ready.exists and \
            self.can_afford(AbilityId.CYBERNETICSCORERESEARCH_PROTOSSAIRWEAPONSLEVEL1) \
            and self.already_pending_upgrade(UpgradeId.PROTOSSAIRWEAPONSLEVEL1) == 0:
            BY = self.structures(UnitTypeId.CYBERNETICSCORE).ready.first
            if BY.is_idle:
                BY.research(UpgradeId.PROTOSSAIRWEAPONSLEVEL1)
                print("research_protossairweapon_level1 at")
                print(self.get_current_run_time_seconds())

    async def research_protossairweapon_level2(self):
        if self.structures(UnitTypeId.CYBERNETICSCORE).ready.exists and \
            self.structures(UnitTypeId.FLEETBEACON).ready.exists and \
            self.can_afford(AbilityId.CYBERNETICSCORERESEARCH_PROTOSSAIRWEAPONSLEVEL2) \
            and self.already_pending_upgrade(UpgradeId.PROTOSSAIRWEAPONSLEVEL2) == 0:
            BY = self.structures(UnitTypeId.CYBERNETICSCORE).ready.first
            if BY.is_idle:
                BY.research(UpgradeId.PROTOSSAIRWEAPONSLEVEL2)
                print("research_protossairweapon_level2 at")
                print(self.get_current_run_time_seconds())

    async def research_protossairweapon_level3(self):
        if self.structures(UnitTypeId.CYBERNETICSCORE).ready.exists and \
            self.structures(UnitTypeId.FLEETBEACON).ready.exists and \
            self.can_afford(AbilityId.CYBERNETICSCORERESEARCH_PROTOSSAIRWEAPONSLEVEL3) \
            and self.already_pending_upgrade(UpgradeId.PROTOSSAIRWEAPONSLEVEL3) == 0:
            BY = self.structures(UnitTypeId.CYBERNETICSCORE).ready.first
            if BY.is_idle:
                BY.research(UpgradeId.PROTOSSAIRWEAPONSLEVEL3)
                print("research_protossairweapon_level3 at")
                print(self.get_current_run_time_seconds())

    async def research_protossairarmor_level1(self):
        if self.structures(UnitTypeId.CYBERNETICSCORE).ready.exists and \
            self.can_afford(AbilityId.CYBERNETICSCORERESEARCH_PROTOSSAIRARMORLEVEL1) \
            and self.already_pending_upgrade(UpgradeId.PROTOSSAIRARMORSLEVEL1) == 0:
            BY = self.structures(UnitTypeId.CYBERNETICSCORE).ready.first
            if BY.is_idle:
                BY.research(UpgradeId.PROTOSSAIRARMORSLEVEL1)
                print("research_protossairarmor_level1 at")
                print(self.get_current_run_time_seconds())

    async def research_protossairarmor_level2(self):
        if self.structures(UnitTypeId.CYBERNETICSCORE).ready.exists and \
            self.structures(UnitTypeId.FLEETBEACON).ready.exists and \
            self.can_afford(AbilityId.CYBERNETICSCORERESEARCH_PROTOSSAIRARMORLEVEL2) \
            and self.already_pending_upgrade(UpgradeId.PROTOSSAIRARMORSLEVEL2) == 0:
            BY = self.structures(UnitTypeId.CYBERNETICSCORE).ready.first
            if BY.is_idle:
                BY.research(UpgradeId.PROTOSSAIRARMORSLEVEL2)
                print("research_protossairarmor_level2 at")
                print(self.get_current_run_time_seconds())

    async def research_protossairarmor_level3(self):
        if self.structures(UnitTypeId.CYBERNETICSCORE).ready.exists and \
            self.structures(UnitTypeId.FLEETBEACON).ready.exists and \
            self.can_afford(AbilityId.CYBERNETICSCORERESEARCH_PROTOSSAIRARMORLEVEL3) \
            and self.already_pending_upgrade(UpgradeId.PROTOSSAIRARMORSLEVEL3) == 0:
            BY = self.structures(UnitTypeId.CYBERNETICSCORE).ready.first
            if BY.is_idle:
                BY.research(UpgradeId.PROTOSSAIRARMORSLEVEL3)
                print("research_protossairarmor_level3 at")
                print(self.get_current_run_time_seconds())

    #VC researches

    async def quick_build_up_VC_tech(self):
        await self.research_zealot_charge()
        await self.research_stalker_blink()
        await self.research_adept_attack_speed()

    async def research_zealot_charge(self):
        if self.structures(UnitTypeId.TWILIGHTCOUNCIL).ready.exists and self.can_afford(AbilityId.RESEARCH_CHARGE) \
            and self.already_pending_upgrade(UpgradeId.CHARGE) == 0:
            VC = self.structures(UnitTypeId.TWILIGHTCOUNCIL).ready.first
            if VC.is_idle:
                VC.research(UpgradeId.CHARGE)
                print("research_zealot_charge at")
                print(self.get_current_run_time_seconds())

    async def research_stalker_blink(self):
        if self.structures(UnitTypeId.TWILIGHTCOUNCIL).ready.exists and self.can_afford(AbilityId.RESEARCH_BLINK) \
            and self.already_pending_upgrade(UpgradeId.BLINKTECH) == 0:
            VC = self.structures(UnitTypeId.TWILIGHTCOUNCIL).ready.first
            if VC.is_idle:
                VC.research(UpgradeId.BLINKTECH)
                print("research_stalker_blink at")
                print(self.get_current_run_time_seconds())

    async def research_adept_attack_speed(self):
        if self.structures(UnitTypeId.TWILIGHTCOUNCIL).ready.exists and self.can_afford(AbilityId.RESEARCH_ADEPTRESONATINGGLAIVES) \
            and self.already_pending_upgrade(UpgradeId.ADEPTPIERCINGATTACK) == 0:
            VC = self.structures(UnitTypeId.TWILIGHTCOUNCIL).ready.first
            if VC.is_idle:
                VC.research(UpgradeId.ADEPTPIERCINGATTACK)
                print("research_adept_attack_speed at")
                print(self.get_current_run_time_seconds())





    # these functions are for overtime situations
    #test economy functions
    async def quick_build_up_economy(self):
        await self.auto_build_workers()
        await self.auto_build_pylons()
        await self.auto_build_gas()
        await self.further_expend()
        await self.distribute_workers()

    async def further_expend(self):
        if self.townhalls.amount >= 1 and not self.already_pending(UnitTypeId.NEXUS) and self.can_afford(UnitTypeId.NEXUS):
            in_production_probe_number = 0
            max_production_probe_number = 0
            for nexus in self.townhalls:
                in_production_probe_number += nexus.assigned_harvesters
                max_production_probe_number += nexus.ideal_harvesters
            if in_production_probe_number >= max_production_probe_number - 2:
                await self.expand_now()

    async def auto_build_workers(self):
        if self.supply_workers < self.get_ideal_amount_of_workers() \
           and self.can_afford(UnitTypeId.PROBE) and \
           self.supply_workers <= 3*(16+3+3):
            for nexus in self.townhalls:
                if nexus.is_ready and nexus.is_idle:
                    nexus.train(UnitTypeId.PROBE)
                    break # so we don't oversupply

    def get_ideal_amount_of_workers(self):
        return 16 * self.townhalls.amount + \
            3* self.structures(UnitTypeId.ASSIMILATOR).amount

    async def auto_build_pylons(self):
        if self.should_build_pylon_for_supply():
            await self.build_one_pylon()

    def should_build_pylon_for_supply(self):
        margin = (self.structures(UnitTypeId.GATEWAY).amount*2 + \
            self.structures(UnitTypeId.WARPGATE).amount*2 + \
            self.structures(UnitTypeId.STARGATE).amount*3 + \
            self.structures(UnitTypeId.ROBOTICSBAY).amount *3)
        need_more_supply = self.supply_left + self.structures(UnitTypeId.PYLON).not_ready.amount * 8 \
           + self.already_pending(UnitTypeId.PYLON) * 8
        return (need_more_supply <= margin) and self.supply_cap < 200
     
    async def auto_build_gas(self):
        if self.townhalls.amount >= 2 and self.can_afford(UnitTypeId.ASSIMILATOR):
            for nexus in self.townhalls.ready:
                vgs = self.vespene_geyser.closer_than(15, nexus)
                for vg in vgs:
                    if not self.gas_buildings.closer_than(1, vg) and \
                        self.can_afford(UnitTypeId.ASSIMILATOR) and \
                        self.already_pending(UnitTypeId.ASSIMILATOR) < 2:
                        worker = self.select_build_worker(vg.position)
                        worker.build(UnitTypeId.ASSIMILATOR, vg)
                        worker.stop(queue=True)











    # this is the Evaluation functions
    async def start_up_evaluation(self):
        if self.enemy_start_up_strategy == ProtossStartUpStrategyId.UNKNOWNSTARTUPSTRATEGY and self.get_current_run_time_seconds() == 115:
            assert self.get_current_run_time_seconds() >= 60 and self.get_current_run_time_seconds() <= 180
            if self.enemy_structures(UnitTypeId.NEXUS).amount >= 2:
                self.enemy_start_up_strategy = ProtossStartUpStrategyId.ECOSTARTUP
                self.enemy_has_second_base = True
            elif self.enemy_structures(UnitTypeId.GATEWAY).amount == 3 and \
                self.enemy_structures(UnitTypeId.CYBERNETICSCORE).amount==0:
                self.enemy_start_up_strategy = ProtossStartUpStrategyId.THREEBGSTARTUP
            elif self.enemy_structures(UnitTypeId.GATEWAY).amount == 2:
                self.enemy_start_up_strategy = ProtossStartUpStrategyId.TWOBGSTARTUP
            else:
                self.enemy_start_up_strategy = ProtossStartUpStrategyId.ONEBGTECH
            print("determined enenmy start up strategy at")
            print(self.get_current_run_time_seconds())
            print(self.enemy_start_up_strategy)
        return

    async def first_stage_evaluation(self):
        return



    # these functions are for first stage strategies within 5 min
    async def build_first_stargate(self):
        if self.structures(UnitTypeId.CYBERNETICSCORE).ready \
           and not self.structures(UnitTypeId.STARGATE) and \
           self.already_pending(UnitTypeId.STARGATE) == 0 and \
           self.can_afford(UnitTypeId.STARGATE):
            pylon = self.structures(UnitTypeId.PYLON).ready.first
            await self.build(UnitTypeId.STARGATE, near=pylon)
            print("build 1st STARGATE at")
            print(self.get_current_run_time_seconds())
        return 

    async def build_first_oracle(self):
        if not self.first_oracle_countered and \
           self.structures(UnitTypeId.STARGATE).ready and \
           self.already_pending(UnitTypeId.ORACLE) == 0 and \
           self.can_afford(UnitTypeId.ORACLE) and\
           self.units(UnitTypeId.ORACLE).amount == 0:
            stargate = self.structures(UnitTypeId.STARGATE).ready.first
            stargate.train(UnitTypeId.ORACLE)
            self.first_oracle = None
            self.oracle_reached_flank_position = False
            self.oracle_begin_attack_workers = False
            self.oracle_intel_gathered = False
            print("build 1st ORACLE at")
            print(self.get_current_run_time_seconds())
        return 

    async def assign_first_oracle(self):
        if self.units(UnitTypeId.ORACLE).ready:
            self.first_oracle = self.units(UnitTypeId.ORACLE).ready.first




    # VS oracle kill worker + gather enemy tech intel
    async def first_oracle_mission(self):
        if self.my_technology_line_strategy == None:
            self.my_technology_line_strategy = ProtossFirstStageStrategyId.VSTECHNOLOGYLINE
        
        await self.get_first_oracle_flank_position()
        await self.build_first_stargate()
        await self.build_first_oracle()
        await self.assign_first_oracle()
        await self.first_oracle_gather_intel()

    async def first_oracle_gather_intel(self):
        await self.update_first_oracle_object()
        if self.first_oracle != None:
            enemy_probes = self.enemy_units(UnitTypeId.PROBE).visible
            if self.oracle_intel_gathered and self.oracle_reached_flank_position:
                if self.first_oracle.position3d.distance_to(self.oracle_flank_position) < 6:
                    if self.first_oracle.energy >= 50:
                        self.oracle_reached_flank_position = False
                        self.oracle_begin_attack_workers = False
                        self.oracle_intel_gathered = False
                elif enemy_probes and self.enemy_units.filter(lambda unit: unit.can_attack_air).visible.amount==0:
                    attack_target = None
                    for enemy_probe in enemy_probes:
                        if enemy_probe.shield_percentage < 0.2:
                            attack_target = enemy_probe
                            break
                    if attack_target == None:
                        attack_target = enemy_probes.closest_to(self.first_oracle.position3d)

                    self.first_oracle.attack(attack_target)
                    print("attack!")
                    return
                else:
                    self.first_oracle_evasive_move_to(self.oracle_flank_position)
                return
                

            if not self.oracle_reached_flank_position:
                self.first_oracle_evasive_move_to(self.oracle_flank_position)
                if self.first_oracle.position3d.distance_to(self.oracle_flank_position) <= 6:
                    self.oracle_reached_flank_position = True
                return
            else:
                danger = self.first_oracle_in_danger()
                enemy_probes = self.enemy_units(UnitTypeId.PROBE).visible
                if self.first_oracle.position3d.distance_to(self.enemy_second_base_location) < 10 and \
                    enemy_probes.amount >=5:
                    self.enemy_second_base_empty = False
                else:
                    self.enemy_second_base_empty = True
                    # print("not worth activate weapon")

                if self.oracle_begin_attack_workers and self.first_oracle.energy >=50:
                    self.first_oracle(AbilityId.BEHAVIOR_PULSARBEAMON)
                    print("activate oracle weapon")
                    return

                target_position = None
                if self.enemy_second_base_empty:
                    target_position = self.enemy_start_locations[0].towards(self.first_nexus, -5)
                else:
                    target_position = self.enemy_second_base_location.towards(self.first_nexus, -5)

                if not danger:
                    if enemy_probes.amount > 3:
                        self.oracle_begin_attack_workers = True
                    else:
                        self.oracle_begin_attack_workers = False

                    if not self.oracle_begin_attack_workers:
                        self.first_oracle.move(target_position)
                        return
                        
                    elif enemy_probes:
                        attack_target = None
                        for enemy_probe in enemy_probes:
                            if enemy_probe.shield_percentage < 0.2:
                                attack_target = enemy_probe
                                break
                        if attack_target == None:
                            attack_target = enemy_probes.closest_to(self.first_oracle.position3d)

                        self.first_oracle.attack(attack_target)
                        print("attack!")
                        return
                else:
                    # print("in danger")
                    if not self.oracle_intel_gathered:
                        if self.enemy_structures(UnitTypeId.TWILIGHTCOUNCIL).visible or \
                            self.enemy_structures(UnitTypeId.STARGATE).visible or \
                            self.enemy_structures(UnitTypeId.ROBOTICSBAY).visible or \
                            self.first_oracle.position3d.distance_to(self.enemy_start_locations[0]) <=8:
                            self.oracle_intel_gathered = True
                            print("intel collected")
                            return
                        self.first_oracle_evasive_move_to(self.enemy_start_locations[0])
                    else:
                        self.first_oracle_evasive_move_to(self.first_nexus.position)
                        return
        return

    def first_oracle_in_danger(self):
        dangerous_structures = self.enemy_structures.filter(lambda unit: unit.can_attack_air).visible   
        if dangerous_structures.amount >= 1:
            self.first_oracle_countered = True
            return True
        for AA in dangerous_structures:
            if AA.position.distance_to(self.first_oracle) < AA.air_range + 2:
                return True

        dangerous_enemys = self.enemy_units.filter(lambda unit: unit.can_attack_air).visible
        if dangerous_enemys.amount >= 3:
            return True
        for AA in dangerous_enemys:
            if AA.position.distance_to(self.first_oracle) < AA.air_range + 4:
                return True
        return False

    async def update_first_oracle_object(self):
        if self.units(UnitTypeId.ORACLE).ready:
            self.first_oracle = self.units(UnitTypeId.ORACLE).ready.first
        else:
            self.first_oracle = None
        return

    async def get_first_oracle_flank_position(self):
        distance = 1.8* self.enemy_second_base_location.distance_to(self.enemy_start_locations[0])
        self.oracle_flank_position = self.enemy_start_locations[0].towards(self.enemy_second_base_location, distance)
        return
        

    def first_oracle_evasive_move_to(self, position):
        nearest_AA_enemys = self.enemy_units.filter(lambda unit: unit.can_attack_air).visible
        nearest_AA_structures = self.enemy_structures.filter(lambda unit: unit.can_attack_air).visible
        nearest_AA_enemy = None
        nearest_AA_structure = None

        if nearest_AA_enemys:
            nearest_AA_enemy = nearest_AA_enemys.closest_to(self.first_oracle.position3d)
        if nearest_AA_structures:
            nearest_AA_structure = nearest_AA_structures.closest_to(self.first_oracle.position3d)

        if nearest_AA_structure != None:
            if nearest_AA_structure.position3d.distance_to(self.first_oracle.position3d) < nearest_AA_structure.air_range + 2:
                self.first_oracle.move(self.first_oracle.position3d.towards(nearest_AA_structure, -8).towards(position, 4))
                print("evasive move")
        elif nearest_AA_enemy != None:
            if nearest_AA_enemy.position3d.distance_to(self.first_oracle.position3d) <= nearest_AA_enemy.air_range + 4:
                self.first_oracle.move(self.first_oracle.position3d.towards(nearest_AA_enemy, -8).towards(position, 4))
                print("evasive move")
        else:
            self.first_oracle.move(position)































    async def zealot_charge_white_ball(self):
        await self.research_gateway_warpgate()
        await self.build_offensive_force()
        await self.build_gateways()
        await self.build_twilightcouncil()
        await self.research_zealot_charge()
        await self.build_templararchive()
        await self.whiteball()


    async def build_gateways(self):
        if self.can_afford(UnitTypeId.GATEWAY) and self.structures(UnitTypeId.PYLON).ready.exists \
           and self.structures(UnitTypeId.GATEWAY).amount + self.structures(UnitTypeId.WARPGATE).amount< 2*self.structures(UnitTypeId.NEXUS).amount:
            if self.structures(UnitTypeId.TWILIGHTCOUNCIL).ready.exists:
                pylon = self.structures(UnitTypeId.PYLON).ready.random
                await self.build(UnitTypeId.GATEWAY, near=pylon)

    async def build_twilightcouncil(self):
        if self.can_afford(UnitTypeId.TWILIGHTCOUNCIL) and self.structures(UnitTypeId.PYLON).ready.exists \
           and not self.structures(UnitTypeId.TWILIGHTCOUNCIL).not_ready.exists and \
           not self.structures(UnitTypeId.TWILIGHTCOUNCIL).ready.exists:
            pylon = self.structures(UnitTypeId.PYLON).ready.random
            await self.build(UnitTypeId.TWILIGHTCOUNCIL, near=pylon)

    async def build_templararchive(self):
        if self.can_afford(UnitTypeId.TEMPLARARCHIVE) and self.structures(UnitTypeId.PYLON).ready.exists \
           and self.structures(UnitTypeId.TWILIGHTCOUNCIL).ready.exists \
           and not self.structures(UnitTypeId.TEMPLARARCHIVE).not_ready.exists and \
           not self.structures(UnitTypeId.TEMPLARARCHIVE).ready.exists:
            pylon = self.structures(UnitTypeId.PYLON).ready.random
            await self.build(UnitTypeId.TEMPLARARCHIVE, near=pylon)

    async def whiteball(self):
        if self.units(UnitTypeId.HIGHTEMPLAR).idle.ready.amount >= 4:
            ht1 = self.units(UnitTypeId.HIGHTEMPLAR).idle.ready.random
            ht2 = next((ht for ht in self.units(UnitTypeId.HIGHTEMPLAR).idle.ready if ht.tag != ht1.tag), None)
            if ht2:
                from s2clientprotocol import raw_pb2 as raw_pb
                from s2clientprotocol import sc2api_pb2 as sc_pb
                command = raw_pb.ActionRawUnitCommand(
                        ability_id=AbilityId.MORPH_ARCHON.value,
                        unit_tags=[ht1.tag, ht2.tag],
                        queue_command=False
                    )
                action = raw_pb.ActionRaw(unit_command=command)
                await self._client._execute(action=sc_pb.RequestAction(
                        actions=[sc_pb.Action(action_raw=action)]
                    ))

    async def build_offensive_force(self):
        for warpgate in self.structures(UnitTypeId.WARPGATE).ready:
            abilities = await self.get_available_abilities(warpgate)

            if AbilityId.WARPGATETRAIN_HIGHTEMPLAR in abilities and \
                self.can_afford(UnitTypeId.HIGHTEMPLAR) and self.supply_left > 0 \
                and self.vespene >= 300:

                pos = self.structures(UnitTypeId.PYLON).furthest_to(self.first_nexus).position.to2.random_on_distance(4)
                placement = await self.find_placement(AbilityId.WARPGATETRAIN_HIGHTEMPLAR, pos, placement_step=1)
                if placement is None:
                    return
                warpgate.warp_in(UnitTypeId.HIGHTEMPLAR, placement)
                continue

            if AbilityId.WARPGATETRAIN_STALKER in abilities and \
                self.can_afford(UnitTypeId.STALKER) and self.supply_left > 0 \
                and self.units(UnitTypeId.STALKER).amount < 3*self.structures(UnitTypeId.NEXUS).amount:

                pos = self.structures(UnitTypeId.PYLON).furthest_to(self.first_nexus).position.to2.random_on_distance(4)
                placement = await self.find_placement(AbilityId.WARPGATETRAIN_STALKER, pos, placement_step=1)
                if placement is None:
                    return
                warpgate.warp_in(UnitTypeId.STALKER, placement)

            elif AbilityId.WARPGATETRAIN_ZEALOT in abilities and \
                self.can_afford(UnitTypeId.ZEALOT) and self.supply_left > 0 \
                and self.units(UnitTypeId.ZEALOT).amount < 7*self.structures(UnitTypeId.NEXUS).amount:

                pos = self.structures(UnitTypeId.PYLON).furthest_to(self.first_nexus).position.to2.random_on_distance(4)
                placement = await self.find_placement(AbilityId.WARPGATETRAIN_ZEALOT, pos, placement_step=1)
                if placement is None:
                    return
                warpgate.warp_in(UnitTypeId.ZEALOT, placement)

            else:
                continue

        for gw in self.structures(UnitTypeId.GATEWAY).ready.idle:
            if self.vespene >= 300:
                if self.can_afford(UnitTypeId.HIGHTEMPLAR) and self.supply_left > 0:
                    gw.train(UnitTypeId.HIGHTEMPLAR)
                    continue
            if self.can_afford(UnitTypeId.STALKER) and self.supply_left > 0 \
                 and self.units(UnitTypeId.STALKER).amount < 3*self.structures(UnitTypeId.NEXUS).amount:
                gw.train(UnitTypeId.STALKER)
            elif self.can_afford(UnitTypeId.ZEALOT) and self.supply_left > 0 \
               and self.units(UnitTypeId.ZEALOT).amount < 7*self.structures(UnitTypeId.NEXUS).amount:
                gw.train(UnitTypeId.ZEALOT)
            else:
                continue


#basic defend and attack

    async def basic_attack_and_defend(self):
        await self.defend_base()
        await self.attack()
        
    async def defend_base(self):
        if self.enemy_units:
            for nexus in self.structures(UnitTypeId.NEXUS):
                enemy_attack_force = self.enemy_units.closer_than(40, nexus)
                if enemy_attack_force:
                    attack_position = enemy_attack_force.closest_to(nexus).position
                    for my_attack_force in self.units.filter(lambda unit: unit.can_attack) \
                        .filter(lambda unit: unit.is_idle):
                        my_attack_force.attack(attack_position)
                    return

    def should_attack(self):
        if (self.supply_army >= 40 + self.structures(UnitTypeId.NEXUS).amount *50 \
           and self.townhalls.amount >= 2) \
           or self.supply_used >= 190:
            self.main_force = self.units.filter(lambda unit: unit.can_attack) \
                .filter(lambda unit: unit.is_idle)

    async def attack(self):
        self.should_attack()
        if self.main_force != None:
            for unit in self.main_force:
                position = None
                if self.enemy_units:
                    position = self.enemy_units.closest_to(unit).position
                if position == None:
                    position = self.enemy_structures.closest_to(unit).position
                if position == None:
                    position = self.enemy_start_locations[0]
                unit.attack(position)