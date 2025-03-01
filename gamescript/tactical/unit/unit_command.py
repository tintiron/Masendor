def process_command(self, target_pos, run_command=False, revert_move=False, enemy=None, other_command=None):
    """Process input order into state and subunit base_target action
    other_command parameter 0 is default command, 1 is natural pause, 2 is order pause"""
    if other_command is None:  # move or melee_attack command
        self.state = 1

        if self.attack_place or (enemy is not None and (self.team != enemy.team)):  # melee_attack
            if self.ammo <= 0 or self.forced_melee:  # no magazine_left to shoot or forced melee_attack command
                self.state = 3  # move to melee
            elif self.ammo > 0:  # have magazine_left to shoot
                self.state = 5  # Move to range melee_attack
            if self.attack_place:  # melee_attack specific location
                self.set_target(target_pos)
                # if self.magazine_left > 0:
                self.base_attack_pos = target_pos
            else:
                self.attack_target = enemy
                self.base_attack_pos = enemy.base_pos
                self.set_target(self.base_attack_pos)

        else:
            self.set_target(target_pos)

        if run_command or self.run_toggle == 1:
            self.state += 1  # run state

        self.command_state = self.state

        self.range_combat_check = False
        self.command_target = self.base_target
        self.new_angle = self.set_rotate()

        if revert_move:  # revert subunit without rotate, cannot run in this state
            self.revert_move()
            # if runcommand or self.run_toggle:
            #     self.state -= 1

        if self.charging:  # change order when attacking will cause authority penalty
            self.leader[0].authority -= self.auth_penalty
            self.auth_recal()

    elif other_command == "Stop" and self.state != 10:  # Pause all action command except combat
        # if self.charging:
        #     self.leader[0].authority -= self.auth_penalty  # decrease authority of the first leader for stop charge
        #     self.auth_recal()  # recal authority

        self.state = 0  # go into idle state
        self.command_state = self.state  # reset command state
        self.set_target(self.front_pos)  # set base_target at self
        self.command_target = self.base_target  # reset command base_target
        self.range_combat_check = False  # reset range combat check
        self.new_angle = self.set_rotate()  # set rotation base_target
