'''
Created on Jul 15, 2017

@author: BrandonMartin
'''

from curses import wrapper
from game import Game
import sys


def main(screen):
    startLevel = 1
    if len(sys.argv) > 1:
        try:
            startLevel = int(sys.argv[1])
        except:
            pass
    g = Game(screen, startLevel)
    x = g.play()
    return x


if __name__ == '__main__':
    sys.stdout.write("\x1b[8;32;26t")
    sys.stdout.flush()
    x = wrapper(main)
    print()
    print('Singles : {}'.format(x[0]))
    print('Doubles : {}'.format(x[1]))
    print('Triples : {}'.format(x[2]))
    print('Tetris  : {}'.format(x[3]))
    print('Score   : {}'.format(x[4]))
    print()
