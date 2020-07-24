from sc2.unit import Unit
from sharpy.plans.acts import ActBase
from sharpy.managers.roles import UnitTask
from sharpy.knowledges import Knowledge
from sc2 import UnitTypeId, AbilityId


class OracleHarass(ActBase):
    def __init__(self):
        super().__init__()
        self.oracle_tag = None
        self.harass_started = False
        self.already_begin_attack = False
        self.reached_position = False

    async def start(self, knowledge: Knowledge):
        await super().start(knowledge)

    async def execute(self) -> bool:
        oracle = self.knowledge.unit_cache.own(UnitTypeId.ORACLE).ready
        position = self.get_first_oracle_flank_position()
        if oracle.amount >= 1:
            self.knowledge.roles.set_task(UnitTask.Reserved, oracle.first)
            self.oracle_tag = oracle.first.tag
            self.harass_started = True

        if self.harass_started:
            harass_oracle: Unit = self.knowledge.unit_cache.by_tag(self.oracle_tag)
            if harass_oracle is not None:
                if not self.reached_position:
                    if harass_oracle.distance_to(position) <= 10 and harass_oracle.energy >= 50:
                        self.reached_position = True
                    elif harass_oracle.shield_percentage >= 0.95:
                        self.oracle_evasive_move_to(position)
                    else:
                        self.oracle_evasive_move_to(self.knowledge.our_zones[0].center_location)
                else:
                    await self.harass_with_oracle()
        return True  # never block

    async def harass_with_oracle(self):
        harass_oracle: Unit = self.knowledge.unit_cache.by_tag(self.oracle_tag)
        if harass_oracle is not None:
            if not self.already_begin_attack:
                enemy_workers = self.knowledge.unit_cache.enemy_in_range(harass_oracle.position3d, 11).of_type(
                    [UnitTypeId.SCV, UnitTypeId.PROBE, UnitTypeId.DRONE, UnitTypeId.MULE]
                )
                # worth activate weapon
                if enemy_workers.amount >= 3 and harass_oracle.energy >= 50:
                    self.already_begin_attack = True
                    self.do(harass_oracle(AbilityId.BEHAVIOR_PULSARBEAMON))
                    return
            if self.already_begin_attack and harass_oracle.energy <= 1:
                self.already_begin_attack = False
                return

            if not self.oracle_in_danger() and self.already_begin_attack:
                enemy_workers = self.knowledge.unit_cache.enemy_in_range(harass_oracle.position3d, 11).of_type(
                    [UnitTypeId.SCV, UnitTypeId.PROBE, UnitTypeId.DRONE, UnitTypeId.MULE]
                )
                if enemy_workers.exists:
                    # try attack the ones that can be one shot killed
                    attack_target = None
                    for worker in enemy_workers:
                        if worker.shield_health_percentage < 0.5:
                            attack_target = worker
                            break
                    if attack_target is None:
                        attack_target = enemy_workers.closest_to(harass_oracle)
                    self.do(harass_oracle.attack(attack_target))
                else:
                    # gather intel
                    self.oracle_evasive_move_to(self.knowledge.enemy_expansion_zones[0].center_location)
            else:
                if harass_oracle.energy <= 2:
                    self.do(harass_oracle(AbilityId.BEHAVIOR_PULSARBEAMOFF))
                    self.already_begin_attack = False
                    self.reached_position = False
                self.oracle_evasive_move_to(self.knowledge.enemy_expansion_zones[0].center_location)

    def oracle_in_danger(self):
        harass_oracle: Unit = self.knowledge.unit_cache.by_tag(self.oracle_tag)
        enemy_anti_air_units = self.knowledge.unit_cache.enemy_in_range(harass_oracle.position3d, 11) \
            .filter(lambda unit: unit.can_attack_air).visible
        for AA in enemy_anti_air_units:
            if AA.position.distance_to(harass_oracle) < AA.air_range + 3:
                return True
        return False

    def oracle_evasive_move_to(self, position):
        harass_oracle: Unit = self.knowledge.unit_cache.by_tag(self.oracle_tag)
        enemy_anti_air_units = self.knowledge.unit_cache.enemy_in_range(harass_oracle.position3d, 11) \
            .filter(lambda unit: unit.can_attack_air).visible

        if enemy_anti_air_units.exists:
            aa = enemy_anti_air_units.closest_to(harass_oracle)
            distance_to_position = harass_oracle.distance_to(position)
            if distance_to_position >= 10:
                self.do(harass_oracle.move(harass_oracle.position3d
                                           .towards(aa, -8).towards(position, 6)))
            else:
                self.do(harass_oracle.move(harass_oracle.position3d
                                           .towards(aa, -8).towards(position, 4)))
        else:
            self.do(harass_oracle.move(position))

    def get_first_oracle_flank_position(self):
        distance = 1.7 * self.knowledge.enemy_expansion_zones[1].center_location. \
            distance_to(self.knowledge.enemy_expansion_zones[0].center_location)
        return self.knowledge.enemy_expansion_zones[0].center_location. \
            towards(self.knowledge.enemy_expansion_zones[1].center_location, distance)