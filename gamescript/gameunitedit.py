import math
import random

import numpy as np
import csv
import ast
import pygame
import pygame.freetype
from pygame.transform import scale

from gamescript import gamelongscript, gamebattalion, gameleader, gamemap

class Previewbox(pygame.sprite.Sprite):
    main_dir = None
    effectimage = None

    def __init__(self, pos):
        self._layer = 1
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = pygame.Surface((500,500))

        self.newcolourlist = {}
        with open(self.main_dir + "/data/map" + '/colourchange.csv', 'r') as unitfile:
            rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
            for row in rd:
                for n, i in enumerate(row):
                    if i.isdigit():
                        row[n] = int(i)
                    elif "," in i:
                        row[n] = ast.literal_eval(i)
                self.newcolourlist[row[0]] = row[1:]

        self.changeterrain(self.newcolourlist[0])

        self.rect = self.image.get_rect(center=pos)

    def changeterrain(self, newterrain):
        self.image.fill(newterrain[1])
        rect = self.image.get_rect(topleft=(0, 0))
        self.image.blit(self.effectimage, rect)  ## Add special filter effect that make it look like old map

class Terrainbox(pygame.sprite.Sprite):
    def __init__(self, pos, image):
        import main
        SCREENRECT = main.SCREENRECT
        self.widthadjust = SCREENRECT.width / 1366
        self.heightadjust = SCREENRECT.height / 768

        self._layer = 13
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = image
        self.rect = self.image.get_rect(topleft=pos)

class Weatherbox(pygame.sprite.Sprite):
    def __init__(self, pos, image):
        import main
        SCREENRECT = main.SCREENRECT
        self.widthadjust = SCREENRECT.width / 1366
        self.heightadjust = SCREENRECT.height / 768

        self._layer = 13
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = image
        self.rect = self.image.get_rect(topleft=pos)

class Filterbox(pygame.sprite.Sprite):
    def __init__(self, pos, image):
        import main
        SCREENRECT = main.SCREENRECT
        self.widthadjust = SCREENRECT.width / 1366
        self.heightadjust = SCREENRECT.height / 768

        self._layer = 13
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = image
        self.rect = self.image.get_rect(topleft=pos)

class Listbox(pygame.sprite.Sprite):
    def __init__(self, pos, image):
        self._layer = 13
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = image
        self.rect = self.image.get_rect(topleft=pos)


class Namelist(pygame.sprite.Sprite):
    def __init__(self, pos, name, subsection, textsize=16):
        self._layer = 14
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.font = pygame.font.SysFont("helvetica", textsize)
        self.image = pygame.Surface((180, 25))  # black corner
        self.image.fill((0, 0, 0))

        #v White body square
        smallimage = pygame.Surface((178, 23))
        smallimage.fill((255, 255, 255))
        smallrect = smallimage.get_rect(topleft=(1, 1))
        self.image.blit(smallimage, smallrect)
        #^ End white body

        #v Troop name text
        textsurface = self.font.render(str(name), 1, (0, 0, 0))
        textrect = textsurface.get_rect(midleft=(3, self.image.get_height() / 2))
        self.image.blit(textsurface, textrect)
        #^ End troop name

        self.subsection = subsection
        self.pos = pos
        self.rect = self.image.get_rect(topleft=self.pos)
#
class Unitpreview(pygame.sprite.Sprite):
    def __init__(self, maingame, position, gameid, squadlist, colour, leader, leaderpos, coa, startangle, team):
        self = gamelongscript.addarmy(squadlist, position, gameid,
                       colour, (maingame.squadwidth, maingame.squadheight), leader+leaderpos, maingame.leaderstat, maingame.gameunitstat, True,
                       coa, False, startangle, 100, 100, team)