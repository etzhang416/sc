import sc2
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.ability_id import AbilityId
from sc2.ids.upgrade_id import UpgradeId
from sc2.ids.buff_id import BuffId
from sc2.unit import Unit
from sc2.units import Units
from sc2.position import Point2

class ChargeZealotRushBot(sc2.BotAI):

    def __init__(self):
        self.ITERATIONS_PER_MINUTE = 165
        
    def get_current_run_time_seconds(self):
        return int(self.time)

    async def on_step(self, iteration):
        await self.distribute_workers()
        await self.basic_attack_and_defend()
        
        if self.get_current_run_time_seconds() < 150:
            await self.default_eco_start_up()
        else: 
            await self.zealot_charge_rush()






#protoss default eco start up
    async def default_eco_start_up(self):
        await self.distribute_workers()
        if self.get_current_run_time_seconds() < 13:
            await self.build_one_worker()
        elif self.get_current_run_time_seconds() < 17:
            await self.build_first_pylon()
        elif self.get_current_run_time_seconds() < 30:
            await self.build_one_worker()
        elif self.get_current_run_time_seconds() < 39:
            await self.build_one_gateway()
        elif self.get_current_run_time_seconds() < 45:
            await self.build_one_worker()
        elif self.get_current_run_time_seconds() < 50:
            await self.build_one_assimilators()
        elif self.get_current_run_time_seconds() < 85:
            await self.build_one_worker()
        elif self.get_current_run_time_seconds() < 95:
            await self.expand()
        elif self.get_current_run_time_seconds() < 107:
            await self.build_one_cyberneticscore()
        elif self.get_current_run_time_seconds() < 109:
            await self.build_one_worker()
        elif self.get_current_run_time_seconds() < 112:
            await self.build_one_assimilators()
        elif self.get_current_run_time_seconds() < 123:
            await self.build_one_worker()
        elif self.get_current_run_time_seconds() < 136:
            await self.build_one_pylon()
        elif self.get_current_run_time_seconds() < 150:
            await self.build_one_stalker()
            
        
    async def build_one_worker(self):
        first_nexus = self.units(UnitTypeId.NEXUS).ready.first
        if self.can_afford(UnitTypeId.PROBE) and first_nexus.is_idle:
            await self.do(first_nexus.train(UnitTypeId.PROBE))

    async def build_first_pylon(self):
        if not self.already_pending(UnitTypeId.PYLON):
            first_nexus = self.units(UnitTypeId.NEXUS).ready.first
            if self.can_afford(UnitTypeId.PYLON):
                await self.build(UnitTypeId.PYLON, \
                                 near=first_nexus.position.towards(self.game_info.map_center, 7))

    async def build_one_pylon(self):
        if not self.already_pending(UnitTypeId.PYLON):
            first_gateway = self.units(UnitTypeId.GATEWAY).ready.first
            if self.can_afford(UnitTypeId.PYLON):
                await self.build(UnitTypeId.PYLON, \
                                 near=first_gateway)

    async def build_one_gateway(self):
        if self.can_afford(UnitTypeId.GATEWAY) and self.units(UnitTypeId.PYLON).ready.exists:
            pylon = self.units(UnitTypeId.PYLON).ready.first
            await self.build(UnitTypeId.GATEWAY, near=pylon)

    async def build_one_assimilators(self):
        for nexus in self.units(UnitTypeId.NEXUS).ready:
            vaspenes = self.state.vespene_geyser.closer_than(12.0, nexus)
            vaspene = vaspenes.first
            if not self.can_afford(UnitTypeId.ASSIMILATOR):
                break
            worker = self.select_build_worker(vaspene.position)
            if worker is None:
                break
            if not self.units(UnitTypeId.ASSIMILATOR).closer_than(1.0, vaspene).exists and \
               not self.already_pending(UnitTypeId.ASSIMILATOR):
                await self.do(worker.build(UnitTypeId.ASSIMILATOR, vaspene))

    async def expand(self):
        if self.can_afford(UnitTypeId.NEXUS):
            await self.expand_now()
            
    async def build_one_cyberneticscore(self):
        if self.units(UnitTypeId.GATEWAY).ready.exists \
           and not self.units(UnitTypeId.CYBERNETICSCORE):
            if self.can_afford(UnitTypeId.CYBERNETICSCORE) \
               and not self.already_pending(UnitTypeId.CYBERNETICSCORE):
                pylon = self.units(UnitTypeId.PYLON).ready.first
                await self.build(UnitTypeId.CYBERNETICSCORE, near=pylon)

    async def build_one_stalker(self):
        for gw in self.units(UnitTypeId.GATEWAY).ready.idle:
            if self.can_afford(UnitTypeId.STALKER) and self.supply_left > 0:
                await self.do(gw.train(UnitTypeId.STALKER))











#zealot_charge_rush 
    async def zealot_charge_rush(self):
        await self.expand2()
        await self.build_offensive_force()
        await self.build_workers()
        await self.build_pylons()
        await self.build_gateways()
        await self.build_twilightcouncil()
        await self.research_advanced_zealot()


    async def build_gateways(self):
        if self.can_afford(UnitTypeId.GATEWAY) and self.units(UnitTypeId.PYLON).ready.exists \
           and len(self.units(UnitTypeId.GATEWAY)) < 1+2*self.units(UnitTypeId.NEXUS).amount:
            if self.units(UnitTypeId.TWILIGHTCOUNCIL).ready.exists:
                pylon = self.units(UnitTypeId.PYLON).ready.random
                await self.build(UnitTypeId.GATEWAY, near=pylon)

    async def build_twilightcouncil(self):
        if self.can_afford(UnitTypeId.TWILIGHTCOUNCIL) and self.units(UnitTypeId.PYLON).ready.exists \
           and not self.units(UnitTypeId.TWILIGHTCOUNCIL).not_ready.exists and \
           not self.units(UnitTypeId.TWILIGHTCOUNCIL).ready.exists:
            pylon = self.units(UnitTypeId.PYLON).ready.random
            await self.build(UnitTypeId.TWILIGHTCOUNCIL, near=pylon)

    async def build_offensive_force(self):
        for gw in self.units(UnitTypeId.GATEWAY).ready.noqueue:
            if self.can_afford(UnitTypeId.ZEALOT) and self.supply_left > 0 \
               and self.units(UnitTypeId.ZEALOT).amount < 7*self.units(UnitTypeId.NEXUS).amount:
                await self.do(gw.train(UnitTypeId.ZEALOT))
            elif self.can_afford(UnitTypeId.STALKER) and self.supply_left > 0 \
                 and self.units(UnitTypeId.STALKER).amount < 3*self.units(UnitTypeId.NEXUS).amount:
                await self.do(gw.train(UnitTypeId.STALKER))
            else:
                break

    async def build_workers(self):
        if (len(self.units(UnitTypeId.NEXUS)) * 16 + 4) > len(self.units(UnitTypeId.PROBE)) \
           and len(self.units(UnitTypeId.PROBE)) <= 50:
            for nexus in self.units(UnitTypeId.NEXUS).ready.filter(lambda unit: unit.is_idle):
                if self.can_afford(UnitTypeId.PROBE):
                    await self.do(nexus.train(UnitTypeId.PROBE))

    async def build_pylons(self):
        if self.supply_left < 5 and self.already_pending(UnitTypeId.PYLON) <= 2:
            gws = self.units(UnitTypeId.GATEWAY).ready
            if gws.exists:
                if self.can_afford(UnitTypeId.PYLON):
                    await self.build(UnitTypeId.PYLON, near=gws.random)

    async def expand2(self):
        if self.can_afford(UnitTypeId.NEXUS) and self.get_current_run_time_seconds() >= 370 \
		and not self.already_pending(UnitTypeId.NEXUS):
            await self.expand_now()

    async def research_advanced_zealot(self):
        if self.units(UnitTypeId.TWILIGHTCOUNCIL).ready.exists and self.can_afford(AbilityId.RESEARCH_CHARGE):
            tlc = self.units(UnitTypeId.TWILIGHTCOUNCIL).ready.first
            await self.do(tlc.research(UpgradeId.CHARGE))










#basic defend and attack

    async def basic_attack_and_defend(self):
        await self.defend_base()
        await self.attack()
        
    async def defend_base(self):
        if self.known_enemy_units:
            for nexus in self.units(UnitTypeId.NEXUS):
                enemy_attack_force = self.known_enemy_units.closer_than(30, nexus)
                if enemy_attack_force:
                    attack_position = enemy_attack_force.closest_to(nexus).position
                    for my_attack_force in self.units.filter(lambda unit: unit.can_attack) \
                        .filter(lambda unit: unit.is_idle):
                        await self.do(my_attack_force.attack(attack_position))

    async def attack(self):
        if self.should_attack():
            for my_attack_force in self.units.filter(lambda unit: unit.can_attack) \
                .filter(lambda unit: unit.is_idle):
                    await self.do(my_attack_force.attack(self.find_target(my_attack_force, self.state)))

    def find_target(self, current_unit, state):
        targets = (self.known_enemy_units | self.known_enemy_structures).filter(lambda unit: unit.can_be_attacked)
        if targets:
            return targets.closest_to(current_unit)
        else:
            return self.enemy_start_locations[0]

    def should_attack(self):
        return self.units(UnitTypeId.ZEALOT).amount >= 6*self.units(UnitTypeId.NEXUS).amount \
           and self.units(UnitTypeId.STALKER).amount >= 3*self.units(UnitTypeId.NEXUS).amount


