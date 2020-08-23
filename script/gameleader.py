import csv
import math
import random
from statistics import mean

import numpy as np
import pygame
import pygame.freetype
from pygame.transform import scale

from RTS import mainmenu

main_dir = mainmenu.main_dir

class leaderdata():
    def __init__(self, img, option):
        self.imgs = img
        self.leaderlist = {}
        with open(main_dir + "\data\leader" + str(option) + '\\historical_leader.csv', 'r') as unitfile:
            rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
            for row in rd:
                for n, i in enumerate(row):
                    if i.isdigit(): row[n] = int(i)
                    # if and n in []:
                    #     if "," in i: row[n] = [int(item) if item.isdigit() else item for item in row[n].split(',')]
                    # else: row[n] = [int(i)]
                self.leaderlist[row[0]] = row[1:]
        unitfile.close()

        self.leaderclass = {}
        with open(main_dir + "\data\leader" + '\\leader_class.csv', 'r') as unitfile:
            rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
            for row in rd:
                for n, i in enumerate(row):
                    if i.isdigit(): row[n] = int(i)
                    # if and n in []:
                    #     if "," in i: row[n] = [int(item) if item.isdigit() else item for item in row[n].split(',')]
                    # else: row[n] = [int(i)]
                self.leaderclass[row[0]] = row[1:]
        unitfile.close()

class leader(pygame.sprite.Sprite):

    def __init__(self, leaderid, squadposition, armyposition, battalion, leaderstat):
        self._layer = 6
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.morale = 100
        stat = leaderstat.leaderlist[leaderid]
        self.gameid = leaderid
        self.name = stat[0]
        self.health = stat[1]
        self.authority = stat[2]
        self.meleecommand = stat[3]
        self.rangecommand = stat[4]
        self.cavcommand = stat[5]
        self.combat = stat[6]
        self.social = leaderstat.leaderclass[stat[7]]
        self.description = stat[-1]
        self.squadpos = squadposition ## squad position is the index of squad in squad sprite loop
        # self.trait = stat
        # self.skill = stat
        self.state = 0 ## 0 = alive, 96 = retreated, 97 = captured, 98 = missing, 99 = wound, 100 = dead
        if self.name == "none": self.state = 100 ## no leader is same as dead so no need to update
        self.battalion = battalion
        # self.mana = stat
        self.gamestart = 0
        self.armyposition = armyposition
        self.baseimgposition = [(133,65),(80,115),(190,115),(133,163)]
        self.imgposition = self.baseimgposition[self.armyposition]
        ## put leader image into leader slot
        self.image = leaderstat.imgs[leaderid].copy()
        self.rect = self.image.get_rect(center=self.imgposition)
        self.image_original = self.image.copy()
        if self.armyposition == 0:
            squadpenal = int((self.squadpos/8)*10)
            self.authority = self.authority - ((self.authority * squadpenal / 100)/2)
            self.deadmorale = 50 ## main general morale lost when die
        else: self.deadmorale = 30 ## other position morale lost

    def update(self, statuslist, squadgroup, dt, viewmode, playerposlist, enemyposlist):
        if self.gamestart == 0:
            self.squad = self.battalion.squadsprite[self.squadpos]
            self.gamestart = 1
        if self.state not in [100]:
            if self.squad.state == 100:
                self.battalion.gamearmy
                squadpenal = int((self.squadpos / 8) * 10)
                self.authority = self.authority - (self.authority * squadpenal / 100)
            if self.health < 0:
                self.state = 100
                # if random.randint(0,1) == 1: self.state = 99 ## chance to become wound instead when hp reach 0
                self.battalion.leader.append(self.battalion.leader.pop(self.armyposition)) ## move leader to last of list when dead
                # if self.battalion.commander == False:
                for squad in self.battalion.squadsprite:
                    squad.basemorale -= self.deadmorale ## decrease all squad morale when leader die depending on position
                # else:
                #     if self.armyposition != 0:
                #         for squad in self.battalion.squadsprite:
                #             squad.basemorale -= self.deadmorale
                for index, leader in enumerate(self.battalion.leader): ## also change army position of all leader in that battalion
                    leader.armyposition =  index ## change army position to new one
                    leader.imgposition = leader.baseimgposition[leader.armyposition]
                    leader.rect = leader.image.get_rect(center=leader.imgposition)
                    leader.deadmorale = 50
                    if leader.armyposition != 0: leader.deadmorale = 30 ## change dead morale according to new position
                self.battalion.commandbuff = [(self.battalion.leader[0].meleecommand - 5) * 0.1, (self.battalion.leader[0].rangecommand - 5) * 0.1,
                                    (self.battalion.leader[0].cavcommand - 5) * 0.1]
                self.authority = 0
                self.meleecommand = 0
                self.rangecommand = 0
                self.cavcommand = 0
                self.combat = 0
                self.social = 0
                pygame.draw.line(self.image, (150, 20, 20), (5,5),(45,35), 5)
                self.battalion.leaderchange = True
