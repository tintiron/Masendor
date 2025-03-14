"""Functions that are performed in subunit update function only for arcade genre"""

import random
import math
import pygame
infinity = float("inf")
equip_set = ("Main", "Sub")


def player_interact(self, mouse_pos, mouse_left_up):
    """Mouse collision detection"""
    if self.rect.collidepoint(mouse_pos):
        self.battle.last_mouseover = self.unit  # last mouse over on this unit
        if self.battle.game_state == "editor" and self.battle.unit_build_slot not in self.battle.battle_ui_updater:
                if self.battle.game_state == "editor" and mouse_left_up and self.battle.click_any is False:
                    self.battle.current_selected = self.unit  # become last selected unit
                    if self.unit.selected is False:
                        self.unit.just_selected = True
                        self.unit.selected = True
                    self.battle.click_any = True


def status_update(self, weather=None):
    """calculate stat from stamina, morale state, skill, status, terrain"""

    if self.red_border and self.unit.selected:  # have red border (taking melee_dmg) on inspect ui, reset image
        self.block.blit(self.block_original, self.corner_image_rect)
        self.red_border = False

    # v reset stat to default and apply morale, stamina, command buff to stat
    if self.max_stamina > 100:
        self.max_stamina = self.max_stamina - (self.timer * 0.05)  # Max stamina gradually decrease over time - (self.timer * 0.05)
        self.stamina75 = self.max_stamina * 0.75
        self.stamina50 = self.max_stamina * 0.5
        self.stamina25 = self.max_stamina * 0.25
        self.stamina5 = self.max_stamina * 0.05

    self.morale = self.base_morale
    self.authority = self.unit.authority  # unit total authority
    self.command_buff = self.unit.command_buff[
                           self.subunit_type] * 100  # command buff from start_set leader according to this subunit type
    self.discipline = self.base_discipline
    self.melee_attack = self.base_melee_attack
    self.melee_def = self.base_melee_def
    self.range_def = self.base_range_def
    self.accuracy = self.base_accuracy
    self.reload = self.base_reload
    self.charge_def = self.base_charge_def
    self.speed = self.base_speed
    self.charge = self.base_charge
    self.shoot_range = self.base_range

    self.crit_effect = 1  # default critical effect
    self.front_dmg_effect = 1  # default frontal melee_dmg
    self.side_dmg_effect = 1  # default side melee_dmg

    self.corner_atk = False  # cannot melee_attack corner enemy by default
    self.temp_full_def = False

    self.auth_penalty = self.base_auth_penalty
    self.hp_regen = self.base_hp_regen
    self.stamina_regen = self.base_stamina_regen
    self.inflict_status = self.base_inflict_status
    self.elem_melee = self.base_elem_melee
    self.elem_range = self.base_elem_range
    # ^ End default stat

    # v Apply status effect from trait
    if len(self.trait) > 1:
        for trait in self.trait.values():
            if 0 not in trait["Status"]:  # 0 value means no trait or not use
                for effect in trait["Status"]:  # apply status effect from trait
                    self.status_effect[effect] = self.status_list[effect].copy()
                    if trait["Buff Range"] > 1:  # status buff range to nearby friend
                        self.status_to_friend(trait[1], effect, self.status_list[effect].copy())
    # ^ End trait

    # v apply effect from weather"""
    weather_temperature = 0
    if weather is not None:
        self.melee_attack += weather.melee_atk_buff
        self.melee_def += weather.melee_def_buff
        self.range_def += weather.range_def_buff
        # self.armour += weather.armour_buff
        self.speed += weather.speed_buff
        self.accuracy += weather.accuracy_buff
        for shoot_range in self.shoot_range:
            shoot_range += weather.range_buff
        self.reload += weather.reload_buff
        self.charge += weather.charge_buff
        self.charge_def += weather.charge_def_buff
        self.hp_regen += weather.hp_regen_buff
        self.stamina_regen += weather.stamina_regen_buff
        self.morale += (weather.morale_buff * self.mental)
        self.discipline += weather.discipline_buff
        if weather.elem[0] != 0:  # Weather can cause elemental effect such as wet
            self.elem_count[weather.elem[0]] += (weather.elem[1] * (100 - self.elem_res[weather.elem[0]]) / 100)
        weather_temperature = weather.temperature
    # ^ End weather

    # v Map feature modifier to stat
    map_feature_mod = self.feature_map.feature_mod[self.feature]
    if map_feature_mod[self.feature_mod + " Speed/Charge Effect"] != 1:  # speed/charge
        speed_mod = map_feature_mod[self.feature_mod + " Speed/Charge Effect"]  # get the speed mod appropriate to subunit type
        self.speed *= speed_mod
        self.charge *= speed_mod

    if map_feature_mod[self.feature_mod + " Combat Effect"] != 1:  # melee melee_attack
        # combat_mod = self.unit.feature_map.feature_mod[self.unit.feature][self.feature_mod + 1]
        self.melee_attack *= map_feature_mod[self.feature_mod + " Combat Effect"]  # get the melee_attack mod appropriate to subunit type

    if map_feature_mod[self.feature_mod + " Defense Effect"] != 1:  # melee/charge defence
        combat_mod = map_feature_mod[self.feature_mod + " Defense Effect"]  # get the defence mod appropriate to subunit type
        self.melee_def *= combat_mod
        self.charge_def *= combat_mod

    self.range_def += map_feature_mod["Range Defense Bonus"]  # range defence bonus from terrain bonus
    self.accuracy -= (map_feature_mod["Range Defense Bonus"] / 2)  # range def bonus block subunit sight as well so less accuracy
    self.discipline += map_feature_mod["Discipline Bonus"]  # discipline defence bonus from terrain bonus

    if 0 not in map_feature_mod["Status"]:  # Some terrain feature can also cause status effect such as swimming in water
        if 1 in map_feature_mod["Status"]:  # Shallow water type terrain
            self.status_effect[31] = self.status_list[31].copy()  # wet
        if 4 in map_feature_mod["Status"] or 5 in map_feature_mod["Status"]:  # Deep water type terrain
            if 5 in map_feature_mod["Status"]:
                self.status_effect[93] = self.status_list[93].copy()  # drench

            if self.weight > 60 or self.stamina <= 0:  # weight too much or tired will cause drowning
                self.status_effect[102] = self.status_list[102].copy()  # Drowning

            elif self.weight > 30:  # Medium weight subunit has trouble travel through water and will sink and progressively lose troops
                self.status_effect[101] = self.status_list[101].copy()  # Sinking

            elif self.weight < 30:  # Lightweight subunit has no trouble travel through water
                self.status_effect[104] = self.status_list[104].copy()  # Swimming

        if 2 in map_feature_mod["Status"]:  # Rot type terrain
            self.status_effect[54] = self.status_list[54].copy()

        if 3 in map_feature_mod["Status"]:  # Poison type terrain
            self.elem_count[4] += ((100 - self.elem_res[4]) / 100)

        if 6 in map_feature_mod["Status"]:  # Mud terrain
            self.status_effect[106] = self.status_list[106].copy()
    # self.hidden += self.unit.feature_map[self.unit.feature][6]
    temp_reach = map_feature_mod["Temperature"] + weather_temperature  # temperature the subunit will change to based on current terrain feature and weather
    # ^ End map feature

    # v Apply effect from skill
    # For list of status and skill effect column index used in status_update see script_other.py load_game_data()
    if len(self.skill_effect) > 0:
        for status in self.skill_effect:  # apply elemental effect to melee_dmg if skill has element
            cal_status = self.skill_effect[status]
            if cal_status["Type"] == 0 and cal_status["Element"] != 0:  # melee elemental effect
                self.elem_melee = cal_status["Element"]
            elif cal_status["Type"] == 1 and cal_status["Element"] != 0:  # range elemental effect
                self.elem_range = cal_status["Element"]
            self.melee_attack = self.melee_attack * cal_status["Melee Attack Effect"]
            self.melee_def = self.melee_def * cal_status["Melee Defence Effect"]
            self.range_def = self.range_def * cal_status["Ranged Defence Effect"]
            self.speed = self.speed * cal_status["Speed Effect"]
            self.accuracy = self.accuracy * cal_status["Accuracy Effect"]
            for shoot_range in self.shoot_range:
                shoot_range *= cal_status["Range Effect"]
            self.reload = self.reload / cal_status[
                "Reload Effect"]  # different from other modifier the higher mod reduce reload time (decrease stat)
            self.charge = self.charge * cal_status["Charge Effect"]
            self.charge_def = self.charge_def + cal_status["Charge Defence Bonus"]
            self.hp_regen += cal_status["HP Regeneration Bonus"]
            self.stamina_regen += cal_status["Stamina Regeneration Bonus"]
            self.morale = self.morale + (cal_status["Morale Bonus"] * self.mental)
            self.discipline = self.discipline + cal_status["Discipline Bonus"]
            # self.sight += cal_status["Sight Bonus"]
            # self.hidden += cal_status["Hidden Bonus"]
            self.crit_effect = self.crit_effect * cal_status["Critical Effect"]
            self.front_dmg_effect = self.front_dmg_effect * cal_status["Damage Effect"]
            if cal_status["Area of Effect"] in (2, 3) and cal_status["Damage Effect"] != 100:
                self.side_dmg_effect = self.side_dmg_effect * cal_status["Damage Effect"]
                if cal_status["Area of Effect"] == 3:
                    self.corner_atk = True  # if aoe 3 mean it can melee_attack enemy on all side

            # v Apply status to friendly if there is one in skill effect
            if 0 not in cal_status["Status"]:
                for effect in cal_status["Status"]:
                    self.status_effect[effect] = self.status_list[effect].copy()
                    if self.status_effect[effect][2] > 1:
                        self.status_to_friend(self.status_effect[effect][2], effect, self.status_list)
            # ^ End apply status to

            self.bonus_morale_dmg += cal_status["Morale Damage"]
            self.bonus_stamina_dmg += cal_status["Stamina Damage"]
            if 0 not in cal_status["Enemy Status"]:  # Apply status effect to enemy from skill to inflict list
                for effect in cal_status["Enemy Status"]:
                    if effect != 0:
                        self.inflict_status[effect] = cal_status["Area of Effect"]
        if 0 in self.skill_effect:
            self.auth_penalty += 0.5  # higher authority penalty when attacking (retreat while charging)
    # ^ End skill effect

    # v Apply effect and modifier from status effect
    # """special status: 0 no control, 1 hostile to all, 2 no retreat, 3 no terrain effect, 4 no melee_attack, 5 no skill, 6 no spell, 7 no exp gain,
    # 7 immune to bad mind, 8 immune to bad body, 9 immune to all effect, 10 immortal""" Not implemented yet
    if len(self.status_effect) > 0:
        for status in self.status_effect:
            cal_status = self.status_list[status]
            self.melee_attack = self.melee_attack * cal_status["Melee Attack Effect"]
            self.melee_def = self.melee_def * cal_status["Melee Defence Effect"]
            self.range_def = self.range_def * cal_status["Ranged Defence Effect"]
            self.armour = self.armour * cal_status["Armour Effect"]
            self.speed = self.speed * cal_status["Speed Effect"]
            self.accuracy = self.accuracy * cal_status["Accuracy Effect"]
            self.reload = self.reload / cal_status["Reload Effect"]
            self.charge = self.charge * cal_status["Charge Effect"]
            self.charge_def += cal_status["Charge Defence Bonus"]
            self.hp_regen += cal_status["HP Regeneration Bonus"]
            self.stamina_regen += cal_status["Stamina Regeneration Bonus"]
            self.morale = self.morale + (cal_status["Morale Bonus"] * self.mental)
            self.discipline += cal_status["Discipline Bonus"]
            # self.sight += cal_status["Sight Bonus"]
            # self.hidden += cal_status["Hidden Bonus"]
            temp_reach += cal_status["Temperature Change"]
            if status == 91:  # All round defence status
                self.temp_full_def = True
    # ^ End status effect

    self.temperature_cal(temp_reach)  # calculate temperature and its effect

    # v Elemental effect
    if self.elem_count != [0, 0, 0, 0, 0]:  # Apply effect if elem threshold reach 50 or 100
        self.elem_count[0] = self.threshold_count(self.elem_count[0], 28, 92)
        self.elem_count[1] = self.threshold_count(self.elem_count[1], 31, 93)
        self.elem_count[2] = self.threshold_count(self.elem_count[2], 30, 94)
        self.elem_count[3] = self.threshold_count(self.elem_count[3], 23, 35)
        self.elem_count[4] = self.threshold_count(self.elem_count[4], 26, 27)
        self.elem_count = [elem - self.timer if elem > 0 else elem for elem in self.elem_count]
    # ^ End elemental effect

    self.morale_state = self.morale / self.max_morale  # for using as modifier to stat
    if self.morale_state > 3 or math.isnan(self.morale_state):  # morale state more than 3 give no more benefit
        self.morale_state = 3

    self.stamina_state = (self.stamina * 100) / self.max_stamina
    self.stamina_state_cal = 1
    if self.stamina != infinity:
        self.stamina_state_cal = self.stamina_state / 100  # for using as modifier to stat

    self.discipline = (self.discipline * self.morale_state * self.stamina_state_cal) + self.unit.leader_social[
        self.grade_name] + (self.authority / 10)  # use morale, stamina, leader social vs grade (+1 to skip class name) and authority
    self.melee_attack = (self.melee_attack * (self.morale_state + 0.1)) * self.stamina_state_cal + self.command_buff  # use morale, stamina and command buff
    self.melee_def = (self.melee_def * (
            self.morale_state + 0.1)) * self.stamina_state_cal + self.command_buff  # use morale, stamina and command buff
    self.range_def = (self.range_def * (self.morale_state + 0.1)) * self.stamina_state_cal + (
            self.command_buff / 2)  # use morale, stamina and half command buff
    self.accuracy = self.accuracy * self.stamina_state_cal + self.command_buff  # use stamina and command buff
    self.reload = self.reload * (2 - self.stamina_state_cal)  # the less stamina, the higher reload time
    self.charge_def = (self.charge_def * (
            self.morale_state + 0.1)) * self.stamina_state_cal + self.command_buff  # use morale, stamina and command buff
    height_diff = (self.height / self.front_height) ** 2  # walking down hill increase speed while walking up hill reduce speed
    self.speed = self.speed * self.stamina_state_cal * height_diff  # use stamina
    self.charge = (self.charge + self.speed) * (
            self.morale_state + 0.1) * self.stamina_state_cal + self.command_buff  # use morale, stamina and command buff

    full_merge_len = len(self.full_merge) + 1
    if full_merge_len > 1:  # reduce discipline if there are overlap subunit
        self.discipline = self.discipline / full_merge_len

    # v Rounding up, add discipline to stat and forbid negative int stat
    discipline_cal = self.discipline / 200
    self.melee_attack = self.melee_attack + (self.melee_attack * discipline_cal)
    self.melee_def = self.melee_def + (self.melee_def * discipline_cal)
    self.range_def = self.range_def + (self.range_def * discipline_cal)
    # self.armour = self.armour
    self.speed = self.speed + (self.speed * discipline_cal / 2)
    # self.accuracy = self.accuracy
    # self.reload = self.reload
    self.charge_def = self.charge_def + (self.charge_def * discipline_cal)
    self.charge = self.charge + (self.charge * discipline_cal)

    if self.melee_attack < 0:  # seem like using if 0 is faster than max(0,)
        self.melee_attack = 0
    if self.melee_def < 0:
        self.melee_def = 0
    if self.range_def < 0:
        self.range_def = 0
    if self.armour < 1:  # Armour cannot be lower than 1
        self.armour = 1
    if self.speed < 1:
        self.speed = 1
        if 105 in self.status_effect:  # collapse state enforce 0 speed
            self.speed = 0
    if self.accuracy < 0:
        self.accuracy = 0
    if self.reload < 0:
        self.reload = 0
    if self.charge < 0:
        self.charge = 0
    if self.charge_def < 0:
        self.charge_def = 0
    if self.discipline < 0:
        self.discipline = 0
    # ^ End rounding up

    self.rotate_speed = self.unit.rotate_speed * 2  # rotate speed for subunit only use for self rotate not subunit rotate related
    if self.state in (0, 99):
        self.rotate_speed = self.speed

    # v cooldown, active and effect timer function
    self.skill_cooldown = {key: val - self.timer for key, val in self.skill_cooldown.items()}  # cooldown decrease overtime
    self.skill_cooldown = {key: val for key, val in self.skill_cooldown.items() if val > 0}  # remove cooldown if time reach 0
    for a, b in self.skill_effect.items():  # Can't use dict comprehension here since value include all other skill stat
        b["Duration"] -= self.timer
    self.skill_effect = {key: val for key, val in self.skill_effect.items() if
                         val["Duration"] > 0 and len(val["Restriction"]) > 0 and self.state in val["Restriction"]}  # remove effect if time reach 0 or restriction state is not met
    for a, b in self.status_effect.items():
        b["Duration"] -= self.timer
    self.status_effect = {key: val for key, val in self.status_effect.items() if val["Duration"] > 0}
    # ^ End timer effect


def state_reset_logic(self, *args):
    """Simply reset to idle state for arcade mode as it use independent action"""
    self.state = 0


def morale_logic(self, dt, parent_state):
    # v Morale check
    if self.max_morale != infinity:
        if self.base_morale < self.max_morale:
            if self.state != 99:  # If not missing start_set leader can replenish morale
                self.base_morale += (dt * self.stamina_state_cal * self.morale_regen)  # Morale replenish based on stamina

            if self.base_morale < 0:  # morale cannot be negative
                self.base_morale = 0

        elif self.base_morale > self.max_morale:
            self.base_morale -= dt  # gradually reduce morale that exceed the starting max amount

        if self.state in (95, 99):  # disobey or broken state, morale gradually decrease until recover
            self.base_morale -= dt * self.mental


def health_stamina_logic(self, dt):
    """Health and stamina calculation"""
    if self.unit_health != infinity:
        if self.hp_regen > 0 and self.unit_health % self.troop_health != 0:  # hp regen cannot resurrect troop only heal to max hp
            alive_hp = self.troop_number * self.troop_health  # max hp possible for the number of alive subunit
            self.unit_health += self.hp_regen * dt  # regen hp back based on time and regen stat
            if self.unit_health > alive_hp:
                self.unit_health = alive_hp  # Cannot exceed health of alive subunit (exceed mean resurrection)
        elif self.hp_regen < 0:  # negative regen can kill
            self.unit_health += self.hp_regen * dt  # use the same as positive regen (negative regen number * dt will reduce hp)
            remain = self.unit_health / self.troop_health
            if remain.is_integer() is False:  # always round up if there is decimal number
                remain = int(remain) + 1
            else:
                remain = int(remain)
            wound = random.randint(0, (self.troop_number - remain))  # chance to be wounded instead of dead
            self.battle.death_troop_number[self.team] += self.troop_number - remain - wound
            self.battle.wound_troop_number[self.team] += wound
            self.troop_number = remain  # Recal number of troop again in case some destroyed from negative regen

        if self.unit_health < 0:
            self.unit_health = 0  # can't have negative hp
        elif self.unit_health > self.max_health:
            self.unit_health = self.max_health  # hp can't exceed max hp (would increase number of troop)

        if self.old_unit_health != self.unit_health:
            remain = self.unit_health / self.troop_health
            if remain.is_integer() is False:  # always round up if there is decimal number
                remain = int(remain) + 1
            else:
                remain = int(remain)
            wound = random.randint(0, (self.troop_number - remain))  # chance to be wounded instead of dead
            self.battle.death_troop_number[self.team] += self.troop_number - remain - wound
            if self.state in (98, 99) and len(self.enemy_front) + len(
                    self.enemy_side) > 0:  # fleeing or broken got captured instead of wound
                self.battle.capture_troop_number[self.team] += wound
            else:
                self.battle.wound_troop_number[self.team] += wound
            self.troop_number = remain  # Recal number of troop again in case some destroyed from negative regen

            # v Health bar
            for index, health in enumerate(self.health_list):
                if self.unit_health > health:
                    if self.last_health_state != abs(4 - index):
                        self.inspect_image_original3.blit(self.health_image_list[index + 1], self.health_image_rect)
                        self.block_original.blit(self.health_image_list[index + 1], self.health_block_rect)
                        self.block.blit(self.block_original, self.corner_image_rect)
                        self.last_health_state = abs(4 - index)
                        self.zoom_scale()
                    break

            self.old_unit_health = self.unit_health

    if self.stamina != infinity:
        if self.stamina < self.max_stamina:
            self.stamina = self.stamina + (dt * self.stamina_regen)  # regen
        else:  # stamina cannot exceed the max stamina
            self.stamina = self.max_stamina

        if self.old_last_stamina != self.stamina:
            for index, stamina in enumerate((self.stamina75, self.stamina50, self.stamina25, self.stamina5, -1)):
                if self.stamina >= stamina:
                    if self.last_stamina_state != abs(4 - index):
                        # if index != 3:
                        self.inspect_image_original3.blit(self.stamina_image_list[index + 6], self.stamina_image_rect)
                        self.zoom_scale()
                        self.block_original.blit(self.stamina_image_list[index + 6], self.stamina_block_rect)
                        self.block.blit(self.block_original, self.corner_image_rect)
                        self.last_stamina_state = abs(4 - index)
                    break

            self.old_last_stamina = self.stamina


def charge_logic(self, parent_state):
    if self.state == 4:  # charge skill only when running to melee
        self.charge_momentum += self.timer * (self.speed / 50)
        if self.charge_momentum >= 5:
            self.use_skill(0)  # Use charge skill
            self.unit.charging = True
            self.charge_momentum = 5

    elif self.charge_momentum > 1:  # reset charge momentum if charge skill not active
        self.charge_momentum -= self.timer * (self.speed / 50)
        if self.charge_momentum <= 1:
            self.unit.charging = False
            self.charge_momentum = 1


def check_skill_condition(self):
    """Check which skill can be used, cooldown, condition state, discipline, stamina are checked.
    charge skill is excepted from this check"""
    self.available_skill = [skill for skill in self.skill if skill not in self.skill_cooldown.keys()
                            and self.discipline >= self.skill[skill]["Discipline Requirement"]
                            and self.stamina > self.skill[skill]["Stamina Cost"] and skill != 0]


def skill_check_logic(self):
    self.check_skill_condition()
    if not self.current_action and self.command_action:  # no current action and has skill command waiting
        command_action = self.command_action[0]
        if "Skill" in command_action:  # use skill and convert command action into skill action name
            if (self.unit_leader and "Leader" in command_action) or \
                    (self.unit_leader is False and "Troop" in command_action):
                skill = int(self.command_action[0][-1])
                if "Weapon" in command_action:
                    skill = self.weapon_skill[self.equipped_weapon][skill]
                    action = self.skill[skill]["Action"].copy()
                    action[0] += " " + command_action[-1]
                elif len(self.troop_skill) > skill:
                    skill = self.troop_skill[skill]
                    action = self.skill[skill]["Action"].copy()
                    if "Action" in action[0]:
                        action[0] += " " + str(0)  # use main hand by default for Action type animation skill
                if skill != 0 and skill in self.available_skill:
                    self.use_skill(skill)
                    self.command_action = action
                    self.unit.input_delay = 1
                else:
                    self.command_action = ()
            elif "Charge" in command_action:
                action = self.skill[0]["Action"]
                action[0] += " " + command_action[0][-1]
                self.command_action = tuple(action)
            else:
                self.command_action = ()


def swap_weapon(self):
    """Change weapon, adjust stat, trait and skill"""
    self.base_melee_def = self.original_melee_def
    self.base_range_def = self.original_range_def
    self.trait = self.original_trait
    self.skill = self.original_skill
    for weapon_index, weapon in enumerate(((self.primary_main_weapon, self.primary_sub_weapon),
                   (self.secondary_main_weapon, self.secondary_sub_weapon))[self.equipped_weapon]):
        self.base_melee_def += self.weapon_data.weapon_list[weapon[0]]["Defense"]
        self.base_range_def += self.weapon_data.weapon_list[weapon[0]]["Defense"]
        self.skill += self.weapon_data.weapon_list[weapon[0]]["Skill"]
        self.trait += self.weapon_data.weapon_list[weapon[0]]["Trait"]
    self.process_trait_skill()

    self.action_list = {key: value for key, value in self.generic_action_data.items() if
                        key in self.weapon_name[self.equipped_weapon]}


def pick_animation(self):
    try:
        if self.current_action:  # pick animation with current action
            if "Action " in self.current_action[0]:
                equip = int(self.current_action[0][-1])
                weapon = self.weapon_name[self.equipped_weapon][equip]
                animation_name = self.race_name + "_" + equip_set[equip] + "_" + self.action_list[weapon]["Common"] + "_" + self.action_list[weapon]["Attack"]
        else:  # use state to pick animation
            state_name = self.subunit_state[self.state]
            animation_name = self.race_name + "_" + self.action_list[self.weapon_name[0][0]]["Common"] + "_" + state_name + "/" + str(self.equipped_weapon)  #TODO change when add change equip

        self.current_animation = {key: value for key, value in self.sprite_pool.items() if animation_name in key}
        self.current_animation = self.current_animation[random.choice(list(self.current_animation.keys()))]
    except:  # animation not found, use default
        self.current_animation = self.sprite_pool[self.race_name + "_Default/" + str(self.equipped_weapon)]
