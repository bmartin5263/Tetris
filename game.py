'''
Created on Aug 21, 2017

@author: BrandonMartin
'''

import threading
import time
import curses
from board import Board


class Game():
    # Locations for Data To Be Drawn
    TETRIS_COR = (16, 14)
    TRIPLES_COR = (16, 17)
    DOUBLES_COR = (16, 20)
    SINGLES_COR = (16, 23)
    LEVEL_COR = (23, 26)
    SCORE_COR = (8, 26)

    LEGAL_INPUT = (curses.KEY_DOWN, curses.KEY_LEFT, curses.KEY_RIGHT, ord('q'), ord(' '), ord('p'),
                   ord('t'), ord('y'))

    BOARD_INPUT = (curses.KEY_DOWN, curses.KEY_LEFT, curses.KEY_RIGHT, ord(' '))

    LEVEL_SCORES = (0, 0, 500, 2500, 7000, 15000, 30000, 60000, 100000, 150000, 220000)
    LEVEL_TIMES = (1000, 1.2, 1, .7, .5, .3, .2, .15, .1, .08, .06)
    #                0    1   2  3  4  5  6  7   8   9  10

    STARTING_LEVEL = 1

    def __init__(self, screen, startLevel):
        self.length = 10  # Cannot be Modified Yet
        self.height = 20  # Cannot be Modified Yet
        self.board = None  # Game Board Object
        self.threads = []  # Player and Computer Threads
        self.lock = threading.RLock()

        self.screen = screen
        curses.halfdelay(1)

        self.rowsToClear = []  # Used By Computer to Draw Row Clear Effects
        self.board = None  # Game Board Object
        self.level = None
        self.blocksPlaced = None
        self.tetrises = None
        self.triples = None
        self.doubles = None
        self.singles = None
        self.lastCommandTime = None

        self.extraTime = False
        self.hasExtraTime = False
        self.isComplete = False
        self.isPaused = False
        self.didLose = False
        self.isSuspended = False

        self.startLevel = startLevel

        ## Calculate Coordinates ##

        self.spaceCoordinates = []
        for x in range(10):
            for y in range(22):
                self.spaceCoordinates.append((x, y))

        self.spaceCoordinatesReversed = []
        for y in range(22):
            for x in range(10):
                self.spaceCoordinatesReversed.append((x, y))

        self.nextCoordinates = []
        self.afterCoordinates = []
        for x in range(9):
            for y in range(2):
                self.nextCoordinates.append((x, y))

        ## Set Up Curses Colors ##

        curses.curs_set(0)
        curses.start_color()
        ### BLOCKS ###
        curses.init_pair(1, 15, curses.COLOR_BLACK)  # No Block / White Text
        curses.init_pair(2, 15, 12)  # Blue Block
        curses.init_pair(3, 15, 11)  # Yellow Block
        curses.init_pair(4, 15, 208)  # Orange Block
        curses.init_pair(5, 15, 10)  # Green Block
        curses.init_pair(6, 15, 13)  # Purple Block
        curses.init_pair(7, 15, 9)  # Red Block
        curses.init_pair(8, 15, 14)  # Cyan Block
        curses.init_pair(16, 15, 199)  # Dead Block
        curses.init_pair(17, 9, 15)
        ### TEXT ###
        curses.init_pair(9, 12, curses.COLOR_BLACK)  # Blue Text
        curses.init_pair(10, 11, curses.COLOR_BLACK)  # Yellow Text
        curses.init_pair(11, 208, curses.COLOR_BLACK)  # Orange Text
        curses.init_pair(12, 10, curses.COLOR_BLACK)  # Green Text
        curses.init_pair(13, 13, curses.COLOR_BLACK)  # Purple Text
        curses.init_pair(14, 9, curses.COLOR_BLACK)  # Red Text
        curses.init_pair(15, 14, curses.COLOR_BLACK)  # Cyan Text

        self.CURSES_COLOR_DICT = {
            'O': curses.color_pair(3),
            'L': curses.color_pair(2),
            'J': curses.color_pair(4),
            'S': curses.color_pair(6),
            'Z': curses.color_pair(5),
            'T': curses.color_pair(8),
            'I': curses.color_pair(7),
        }

    def newGame(self):
        '''Initializes Game with a blank Board and zero score.'''

        self.board = Board()
        self.screen.erase()
        self.singles = 0
        self.doubles = 0
        self.triples = 0
        self.tetrises = 0
        self.level = self.startLevel
        self.blocksPlaced = 0
        self.score = self.LEVEL_SCORES[self.startLevel]
        self.isComplete = False
        self.isPaused = False
        self.didLose = False
        self.isSuspended = False
        self.extraTime = False
        self.hasExtraTime = False

    def levelUpgrade(self):
        if self.level < 10:
            levelToUpgrade = self.level + 1
            while (self.score >= self.LEVEL_SCORES[levelToUpgrade]):
                levelToUpgrade += 1
            return levelToUpgrade - (self.level + 1)
        else:
            return 0

    def updateLevel(self, amount):
        if 0 <= self.level + amount <= 10:
            self.level += amount

            for i in range(2):
                i
                self.drawBoarder(14)
                time.sleep(.1)
                self.drawBoarder(1)
                time.sleep(.1)

            if self.level > 6:
                self.extraTime = True
            else:
                self.extraTime = False

    def updateScore(self, amount):
        self.score += amount

    def pauseGame(self):
        if self.isPaused:
            self.drawEntireBoard(False)
            self.isPaused = False
        else:
            self.drawEntireBoard(True)
            self.isPaused = True

    def updateRows(self, rowsCleared):
        if rowsCleared == 1:
            self.singles += 1
            self.updateScore(200 * self.level)
        elif rowsCleared == 2:
            self.doubles += 1
            self.updateScore(600 * self.level)
        elif rowsCleared == 3:
            self.triples += 1
            self.updateScore(1500 * self.level)
        elif rowsCleared == 4:
            self.tetrises += 1
            self.updateScore(2500 * self.level)

    def drawBoarder(self, color=1):
        self.lock.acquire()
        self.screen.addstr(0, 0, '   TETRIS!', curses.color_pair(color))
        self.screen.addstr(0, 3, 'T', curses.color_pair(14))
        self.screen.addstr(0, 4, 'E', curses.color_pair(11))
        self.screen.addstr(0, 5, 'T', curses.color_pair(10))
        self.screen.addstr(0, 6, 'R', curses.color_pair(12))
        self.screen.addstr(0, 7, 'I', curses.color_pair(9))
        self.screen.addstr(0, 8, 'S', curses.color_pair(15))
        self.screen.addstr(0, 9, '!', curses.color_pair(13))

        self.screen.addstr(1, 0, '  ♦♦=====♦♦', curses.color_pair(color))

        self.screen.addstr(2, 0, '  ||', curses.color_pair(color))
        self.screen.addstr(2, 9, '||', curses.color_pair(color))

        self.screen.addstr(3, 0, '♦♦♦♦', curses.color_pair(color))
        self.screen.addstr(3, 9, '♦♦♦♦♦ ♦[AFTER]--♦', curses.color_pair(color))
        self.screen.addstr(3, 17, 'AFTER', curses.color_pair(10))

        self.screen.addstr(4, 0, '||', curses.color_pair(color))
        self.screen.addstr(4, 12, '|| |', curses.color_pair(color))
        self.screen.addstr(4, 25, '|', curses.color_pair(color))

        self.screen.addstr(5, 0, '||', curses.color_pair(color))
        self.screen.addstr(5, 12, '|| |', curses.color_pair(color))
        self.screen.addstr(5, 25, '|', curses.color_pair(color))

        self.screen.addstr(6, 0, '||', curses.color_pair(color))
        self.screen.addstr(6, 12, '|| ♦---------♦', curses.color_pair(color))

        self.screen.addstr(7, 0, '||', curses.color_pair(color))
        self.screen.addstr(7, 12, '|| ♦[NEXT]---♦', curses.color_pair(color))
        self.screen.addstr(7, 17, 'NEXT', curses.color_pair(10))

        self.screen.addstr(8, 0, '||', curses.color_pair(color))
        self.screen.addstr(8, 12, '|| |', curses.color_pair(color))
        self.screen.addstr(8, 25, '|', curses.color_pair(color))

        self.screen.addstr(9, 0, '||', curses.color_pair(color))
        self.screen.addstr(9, 12, '|| |', curses.color_pair(color))
        self.screen.addstr(9, 25, '|', curses.color_pair(color))

        self.screen.addstr(10, 0, '||', curses.color_pair(color))
        self.screen.addstr(10, 12, '|| ♦---------♦', curses.color_pair(color))

        self.screen.addstr(11, 0, '||', curses.color_pair(color))
        self.screen.addstr(11, 12, '||', curses.color_pair(color))

        self.screen.addstr(12, 0, '||', curses.color_pair(color))
        self.screen.addstr(12, 12, '|| ♦[SCORE]--♦', curses.color_pair(color))
        self.screen.addstr(12, 17, 'SCORE', curses.color_pair(10))

        self.screen.addstr(13, 0, '||', curses.color_pair(color))
        self.screen.addstr(13, 12, '|| |TETRIS   |', curses.color_pair(color))
        self.screen.addstr(13, 16, 'TETRIS', curses.color_pair(9))

        self.screen.addstr(14, 0, '||', curses.color_pair(color))
        self.screen.addstr(14, 12, '|| |', curses.color_pair(color))
        self.screen.addstr(14, 25, '|', curses.color_pair(color))

        self.screen.addstr(15, 0, '||', curses.color_pair(color))
        self.screen.addstr(15, 12, '|| |', curses.color_pair(color))
        self.screen.addstr(15, 25, '|', curses.color_pair(color))

        self.screen.addstr(16, 0, '||', curses.color_pair(color))
        self.screen.addstr(16, 12, '|| |TRIPLE   |', curses.color_pair(color))
        self.screen.addstr(16, 16, 'TRIPLE', curses.color_pair(9))

        self.screen.addstr(17, 0, '||', curses.color_pair(color))
        self.screen.addstr(17, 12, '|| |', curses.color_pair(color))
        self.screen.addstr(17, 25, '|', curses.color_pair(color))

        self.screen.addstr(18, 0, '||', curses.color_pair(color))
        self.screen.addstr(18, 12, '|| |', curses.color_pair(color))
        self.screen.addstr(18, 25, '|', curses.color_pair(color))

        self.screen.addstr(19, 0, '||', curses.color_pair(color))
        self.screen.addstr(19, 12, '|| |DOUBLE   |', curses.color_pair(color))
        self.screen.addstr(19, 16, 'DOUBLE', curses.color_pair(9))

        self.screen.addstr(20, 0, '||', curses.color_pair(color))
        self.screen.addstr(20, 12, '|| |', curses.color_pair(color))
        self.screen.addstr(20, 25, '|', curses.color_pair(color))

        self.screen.addstr(21, 0, '||', curses.color_pair(color))
        self.screen.addstr(21, 12, '|| |', curses.color_pair(color))
        self.screen.addstr(21, 25, '|', curses.color_pair(color))

        self.screen.addstr(22, 0, '||', curses.color_pair(color))
        self.screen.addstr(22, 12, '|| |SINGLE   |', curses.color_pair(color))
        self.screen.addstr(22, 16, 'SINGLE', curses.color_pair(9))

        self.screen.addstr(23, 0, '||', curses.color_pair(color))
        self.screen.addstr(23, 12, '|| |', curses.color_pair(color))
        self.screen.addstr(23, 25, '|', curses.color_pair(color))

        self.screen.addstr(24, 0, '♦♦==========♦♦ ♦---------♦', curses.color_pair(color))

        self.screen.addstr(25, 0, '♦========================♦', curses.color_pair(color))

        self.screen.addstr(26, 0, '|Score:', curses.color_pair(color))
        self.screen.addstr(26, 16, 'Level:', curses.color_pair(color))
        self.screen.addstr(26, 25, '|', curses.color_pair(color))
        self.screen.addstr(26, 1, 'Score:', curses.color_pair(12))
        self.screen.addstr(26, 16, 'Level:', curses.color_pair(12))

        self.screen.addstr(27, 0, '|------------------------|', curses.color_pair(color))
        self.screen.addstr(28, 0, '|Rotate: space   Drop: d |', curses.color_pair(color))
        self.screen.addstr(28, 1, 'Rotate:', curses.color_pair(14))
        self.screen.addstr(28, 17, 'Drop:', curses.color_pair(14))
        self.screen.addstr(29, 0, '|  Quit: q      Pause: p |', curses.color_pair(color))
        self.screen.addstr(29, 3, 'Quit:', curses.color_pair(14))
        self.screen.addstr(29, 16, 'Pause:', curses.color_pair(14))
        self.screen.addstr(30, 0, '♦========================♦', curses.color_pair(color))
        self.screen.refresh()
        self.lock.release()

    def drawEntireBoard(self, hideBoard=False):
        self.lock.acquire()
        for coordinate in self.spaceCoordinates:
            symbolInformation = self.board.getCell(coordinate, 0)
            if hideBoard and symbolInformation != 'X':
                symbolInformation = ' '
            if symbolInformation != 'X':
                if symbolInformation in self.CURSES_COLOR_DICT.keys():
                    self.screen.addstr(23 - coordinate[1], coordinate[0] + 2, ' ',
                                       self.CURSES_COLOR_DICT[symbolInformation])
                else:
                    self.screen.addstr(23 - coordinate[1], coordinate[0] + 2, str(symbolInformation))
                self.screen.refresh()
        if hideBoard:
            self.screen.addstr(12, 4, 'PAUSED', curses.A_BLINK)
        self.lock.release()

    def updateBoard(self, changes):
        self.lock.acquire()
        if changes != None:
            for coordinate in changes:
                symbolInformation = self.board.getCell(coordinate, 0)
                if symbolInformation in self.CURSES_COLOR_DICT.keys():
                    self.screen.addstr(23 - coordinate[1], coordinate[0] + 2, ' ',
                                       self.CURSES_COLOR_DICT[symbolInformation])
                else:
                    self.screen.addstr(23 - coordinate[1], coordinate[0] + 2, str(symbolInformation))
            self.screen.refresh()
        self.lock.release()

    def drawData(self):
        for coordinate in self.nextCoordinates:
            nextSymbol = self.board.getCell(coordinate, 1)
            afterSymbol = self.board.getCell(coordinate, 2)
            if nextSymbol in self.CURSES_COLOR_DICT.keys():
                self.screen.addstr(9 - coordinate[1], coordinate[0] + 16, ' ', self.CURSES_COLOR_DICT[nextSymbol])
            else:
                self.screen.addstr(9 - coordinate[1], coordinate[0] + 16, str(nextSymbol))
            if afterSymbol in self.CURSES_COLOR_DICT.keys():
                self.screen.addstr(5 - coordinate[1], coordinate[0] + 16, ' ', self.CURSES_COLOR_DICT[afterSymbol])
            else:
                self.screen.addstr(5 - coordinate[1], coordinate[0] + 16, str(afterSymbol))


                ### Lines Cleared ###
        self.screen.addstr(Game.TETRIS_COR[1], Game.TETRIS_COR[0], str(self.tetrises))
        self.screen.addstr(Game.TRIPLES_COR[1], Game.TRIPLES_COR[0], str(self.triples))
        self.screen.addstr(Game.DOUBLES_COR[1], Game.DOUBLES_COR[0], str(self.doubles))
        self.screen.addstr(Game.SINGLES_COR[1], Game.SINGLES_COR[0], str(self.singles))

        self.screen.addstr(Game.LEVEL_COR[1], Game.LEVEL_COR[0], str('  '))
        self.screen.addstr(Game.LEVEL_COR[1], Game.LEVEL_COR[0], str(self.level))
        self.screen.addstr(Game.SCORE_COR[1], Game.SCORE_COR[0], str(self.score))
        self.screen.refresh()

    def effectClearRow(self):
        for i in range(5):
            if len(self.rowsToClear) >= 3:
                delay = .05
            elif len(self.rowsToClear) == 2:
                delay = .07
            else:
                delay = .1
            for rowNum in self.rowsToClear:
                left = 4 - i
                right = 5 + i
                self.screen.addstr(23 - rowNum, left + 2, ' ', curses.color_pair(16))
                self.screen.addstr(23 - rowNum, right + 2, ' ', curses.color_pair(16))
                self.screen.refresh()
                time.sleep(delay)

    def effectGameOver(self):
        for coordinate in self.spaceCoordinatesReversed:
            symbol = self.board.getCell(coordinate, 0)
            if symbol not in [' ', 'X']:
                self.screen.addstr(23 - coordinate[1], coordinate[0] + 2, ' ', curses.color_pair(16))
                self.screen.refresh()
                time.sleep(.02)

        self.screen.addstr(12, 2, "GAME OVER!", curses.color_pair(17))
        self.screen.addstr(13, 2, "          ", curses.color_pair(17))
        self.screen.addstr(14, 2, "  SCORE:  ", curses.color_pair(17))
        self.screen.addstr(15, 2, "{}{}".format(str(self.score), " " * (10 - len(str(self.score)))),
                           curses.color_pair(17))
        self.screen.refresh()
        curses.beep()
        time.sleep(1)
        curses.flushinp()

    ### INPUT HANDLING ###

    def getInput(self, idNum):
        if idNum == 0:
            while not self.isComplete and not self.didLose:
                command = self.getPlayerInput()
                requestType = ''
                if command in Game.LEGAL_INPUT:
                    if command in Game.BOARD_INPUT:
                        requestType = 'board'
                    else:
                        requestType = 'game'
                    if command == ord('q'):
                        self.isComplete = True
                        return
                    elif command == ord('p'):
                        self.pauseGame()
                    elif command == ord('t'):
                        self.updateLevel(-1)
                    elif command == ord('y'):
                        self.updateLevel(1)
                    else:
                        if not self.isPaused and not self.isSuspended:
                            self.makeRequest(0, command, requestType)

        if idNum == 1:
            while not self.isComplete and not self.didLose:
                time.sleep(.01)
                if len(self.rowsToClear) > 0:
                    if not self.isPaused:
                        self.makeRequest(1, 'clear', 'data')
                elapsedTime = time.time() - self.lastCommandTime
                if self.hasExtraTime:
                    if elapsedTime >= .2:
                        if not self.isPaused:
                            self.hasExtraTime = False
                            self.makeRequest(1, curses.KEY_DOWN)
                else:
                    if elapsedTime >= Game.LEVEL_TIMES[self.level]:
                        if not self.isPaused:
                            self.makeRequest(1, curses.KEY_DOWN)

    def getPlayerInput(self):
        while not self.isComplete:
            curses.flushinp()
            k = self.screen.getch()
            return k

    def makeRequest(self, pType, command, requestType='board'):

        if requestType == 'data':
            self.lock.acquire()
            if command == 'clear':
                self.isSuspended = True
                self.effectClearRow()
                command = 'delete'
                requestType = 'board'
                self.rowsToClear = []
                self.isSuspended = False

            self.lock.release()

        if requestType == 'board':
            self.lock.acquire()

            modifications = self.board.command(command)

            if modifications['score']:
                self.drawEntireBoard()
            else:
                self.updateBoard(modifications['cells'])
            if modifications['valid']:
                self.lastCommandTime = time.time()

            self.didLose = modifications['end'] or self.didLose  # or statement prevents didLose from being rewritten
            self.rowsToClear = modifications['clear']

            if modifications['next']:
                self.updateScore(15 * self.level)
                self.blocksPlaced += 1

            if modifications['score'] > 0:
                self.updateRows(modifications['score'])
                if self.score > 500:
                    self.drawData()
                    levelUps = self.levelUpgrade()
                    if levelUps > 0:
                        self.updateLevel(levelUps)

            if modifications['bottom'] and self.extraTime:
                if self.extraTime:
                    self.hasExtraTime = True
            else:
                self.hasExtraTime = False

            self.lock.release()

        self.drawData()

    def createThreads(self):
        '''Creates humanThread for user input and computerThread for automatic drops
            & effects handling.'''
        self.threads = []
        humanThread = threading.Thread(target=self.getInput, args=(0,))
        computerThread = threading.Thread(target=self.getInput, args=(1,))
        self.threads.append(humanThread)
        self.threads.append(computerThread)

    def startThreads(self):
        '''Starts humanThread and computerThread and waits for them to terminate.'''
        self.lastCommandTime = time.time()
        for t in self.threads:
            t.start()
        for t in self.threads:
            t.join()

        curses.nocbreak()
        curses.cbreak()
        if self.didLose:
            self.effectGameOver()
            self.screen.refresh()
            self.screen.getkey()

    def play(self):
        for i in range(1):
            self.newGame()
            self.drawBoarder()
            self.drawEntireBoard()
            self.drawData()
            self.createThreads()
            self.startThreads()
        return (self.singles, self.doubles, self.triples, self.tetrises, self.score)
