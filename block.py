'''
Created on Jul 15, 2017

@author: BrandonMartin
'''

import random


class Block():

    DEFAULTS = {
        'L': {'body': [(0, 0), (0, 1), (1, 1), (2, 1)], 'color': 'orange'},
        'J': {'body': [(0, 1), (1, 1), (2, 0), (2, 1)], 'color': 'blue'},
        'S': {'body': [(0, 0), (1, 0), (1, 1), (2, 1)], 'color': 'purple'},
        'Z': {'body': [(0, 1), (1, 1), (1, 0), (2, 0)], 'color': 'green'},
        'I': {'body': [(0, 0), (1, 0), (2, 0), (3, 0)], 'color': 'red'},
        'O': {'body': [(0, 0), (0, 1), (1, 0), (1, 1)], 'color': 'yellow'},
        'T': {'body': [(0, 1), (1, 0), (1, 1), (2, 1)], 'color': 'cyan'},
    }

    BODIES = {
        'L': [[(0, 0), (0, 1), (1, 1), (2, 1)], [(0, 0), (0, 1), (0, 2), (1, 0)], [(0, 0), (1, 0), (2, 0), (2, 1)],
              [(0, 2), (1, 2), (1, 1), (1, 0)]],
        'J': [[(0, 1), (1, 1), (2, 0), (2, 1)], [(0, 0), (0, 1), (0, 2), (1, 2)], [(0, 0), (0, 1), (1, 0), (2, 0)],
              [(0, 0), (1, 0), (1, 1), (1, 2)]],
        'S': [[(0, 0), (1, 0), (1, 1), (2, 1)], [(0, 1), (0, 2), (1, 1), (1, 0)]],
        'Z': [[(0, 1), (1, 1), (1, 0), (2, 0)], [(0, 0), (0, 1), (1, 1), (1, 2)]],
        'I': [[(0, 0), (1, 0), (2, 0), (3, 0)], [(2, 0), (2, 1), (2, 2), (2, 3)]],
        'T': [[(0, 1), (1, 0), (1, 1), (2, 1)], [(0, 0), (0, 1), (0, 2), (1, 1)], [(0, 0), (1, 0), (1, 1), (2, 0)],
              [(1, 1), (2, 0), (2, 1), (2, 2)]],
        'O': [[(0, 0), (0, 1), (1, 0), (1, 1)]]
    }

    def __init__(self, blockType=None, body=None, blockCopy=None):
        if blockCopy == None:
            if blockType == None:
                self.type = random.choice(list(Block.DEFAULTS.keys()))
            else:
                self.type = blockType

            if body == None:
                self.body = Block.DEFAULTS[self.type]['body']
            else:
                self.body = self.nextBody(body)

            self.color = Block.DEFAULTS[self.type]['color']

        else:
            self.type = blockCopy.type
            self.color = blockCopy.color
            self.body = blockCopy.body

    def rotate(self):
        b = Block(blockType=self.type, body=self.body)
        return b

    def listBody(self, coordinates):
        output = []
        for piece in self.body:
            output.append([coordinates[0] + piece[0], coordinates[1] + piece[1]])
        return output

    def nextBody(self, body):
        bodies = Block.BODIES[self.type]
        bodyIndex = bodies.index(body) + 1
        if bodyIndex == len(bodies):
            return bodies[0]
        else:
            return bodies[bodyIndex]