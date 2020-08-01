from sc2.unit import Unit
from sharpy.plans.acts import ActBase
from sharpy.managers.roles import UnitTask
from sharpy.knowledges import Knowledge
from sc2 import UnitTypeId, AbilityId


class WarpPrismHarass(ActBase):
    def __init__(self):
        super().__init__()
        self.prism_tag = None
        self.harass_started = False
        self.already_begin_drop = False
        self.reached_position = False

    async def start(self, knowledge: Knowledge):
        await super().start(knowledge)

    async def execute(self) -> bool:
        prism = self.knowledge.unit_cache.own(UnitTypeId.WARPPRISM).ready
        position = self.get_flank_position()
        if prism.amount >= 1:
            if self.prism_tag is None:
                self.prism_tag = prism.first.tag
            self.harass_started = True

        if self.harass_started:
            harass_prism: Unit = self.knowledge.unit_cache.by_tag(self.prism_tag)
            if harass_prism is not None:
                self.knowledge.roles.set_task(UnitTask.Reserved, harass_prism)
                if not self.reached_position:
                    if harass_prism.distance_to(position) <= 4:
                        self.reached_position = True
                    elif harass_prism.shield_percentage >= 0.68:
                        self.prism_evasive_move_to(position)
                    else:
                        if self.knowledge.our_zones:
                            base = self.knowledge.our_zones[0].center_location
                            self.prism_evasive_move_to(base)
                else:
                    await self.harass_with_prism()
        return True  # never block

    async def harass_with_prism(self):
        prism: Unit = self.knowledge.unit_cache.by_tag(self.prism_tag)
        if prism is not None:
            if not self.already_begin_drop:
                drop_zone = self.knowledge.enemy_expansion_zones[0].behind_mineral_position_center
                if prism.distance_to(drop_zone) <= 2:
                    self.do(prism(AbilityId.MORPH_WARPPRISMPHASINGMODE))
                    self.already_begin_drop = True
                    return
                else:
                    self.prism_evasive_move_to(drop_zone)
            else:
                # in danger
                if self.should_retreat():
                    self.do(prism(AbilityId.MORPH_WARPPRISMTRANSPORTMODE))
                    self.reached_position = False
                    self.already_begin_drop = False
                    return
                else:
                    # keep warp
                    warpgates = self.cache.own(UnitTypeId.WARPGATE)
                    for warpgate in warpgates.ready:
                        if await self.ready_to_warp(warpgate):
                            pos = prism.position.random_on_distance(6)
                            placement = await self.ai.find_placement(AbilityId.WARPGATETRAIN_ZEALOT, pos,
                                                                     placement_step=1)
                            if placement is None:
                                # return ActionResult.CantFindPlacementLocation
                                self.knowledge.print("can't find place to warp in")
                                return
                            self.do(warpgate.warp_in(UnitTypeId.ZEALOT, placement))

    def should_retreat(self):
        prism: Unit = self.knowledge.unit_cache.by_tag(self.prism_tag)

        number_of_AA_units = 0
        number_of_AG_units = self.knowledge.unit_cache.enemy_in_range(prism.position3d, 11).amount -\
            self.knowledge.unit_cache.enemy_in_range(prism.position3d, 11).of_type(
                    [UnitTypeId.SCV, UnitTypeId.PROBE, UnitTypeId.DRONE, UnitTypeId.MULE]
                ).amount

        enemy_anti_air_units = self.knowledge.unit_cache.enemy_in_range(prism.position3d, 11) \
            .filter(lambda unit: unit.can_attack_air).visible

        for AA in enemy_anti_air_units:
            if AA.position.distance_to(prism) < AA.air_range + 2:
                number_of_AA_units += 1

        if number_of_AA_units >= 4 and prism.shield_health_percentage <= 0.55:
            return True
        elif number_of_AG_units >= 5:
            return True
        else:
            return False

    def prism_evasive_move_to(self, position_to):
        prism: Unit = self.knowledge.unit_cache.by_tag(self.prism_tag)
        enemy_anti_air_units = self.knowledge.unit_cache.enemy_in_range(prism.position3d, 11) \
            .filter(lambda unit: unit.can_attack_air).visible

        if enemy_anti_air_units.exists:
            position = prism.position3d
            for aa in enemy_anti_air_units:
                distance = prism.distance_to(aa.position3d)
                amount_of_evade = 11 - distance
                position = position.towards(aa, - amount_of_evade)
            # after the for loop, position is the best vector away from enemy
            distance_to_best_evade_point = prism.distance_to(position)
            should_go = position.towards(position_to, 1 + distance_to_best_evade_point*1.5)
            self.do(prism.move(should_go))
        else:
            self.do(prism.move(position_to))

    def get_flank_position(self):
        distance = 1.7 * self.knowledge.enemy_expansion_zones[1].center_location. \
            distance_to(self.knowledge.enemy_expansion_zones[0].center_location)
        return self.knowledge.enemy_expansion_zones[0].center_location. \
            towards(self.knowledge.enemy_expansion_zones[1].center_location, distance)

    async def ready_to_warp(self, warpgate: Unit):
        # all the units have the same cooldown anyway so let's just look at ZEALOT
        return self.cd_manager.is_ready(warpgate.tag, AbilityId.WARPGATETRAIN_ZEALOT)
