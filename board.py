from block import Block
import curses

class Board():

    MOVEMENTS = (curses.KEY_RIGHT, curses.KEY_DOWN, curses.KEY_LEFT)
    ROTATE = ord(' ')
    ORIGIN = [3, 20]
    NEXT_ORIGIN = [3, 0]

    def __init__(self, height=20, length=10):
        self.height = height
        self.length = length

        self.board = None
        self.nextGrid = None
        self.afterGrid = None

        self.coordinates = [0, 0]
        self.currentBlock = None
        self.nextBlock = None
        self.afterBlock = None

        self.extraTime = False
        self.hasExtraTime = False

        self.rowsCleared = 0
        self.rowsToClear = []

        self.newBoard()

    def newBoard(self):
        self.board = [None] * (self.height + 2)
        self.nextGrid = [None] * (2)
        self.afterGrid = [None] * (2)

        for i in range(self.height + 2):
            self.board[i] = [' '] * self.length

        for i in range(2):
            self.nextGrid[i] = [' '] * 9
            self.afterGrid[i] = [' '] * 9

        self.board[20] = ['X', 'X', ' ', ' ', ' ', ' ', ' ', 'X', 'X', 'X']
        self.board[21] = ['X', 'X', ' ', ' ', ' ', ' ', ' ', 'X', 'X', 'X']

        self.currentBlock = Block()
        self.nextBlock = Block()
        self.afterBlock = Block()
        self.moveBlocks()
        self.coordinates = Board.ORIGIN

        self.placeBlock(self.currentBlock, self.coordinates)

    def command(self, command):
        result = {'cells': [],
                  'score': 0,
                  'clear': [],
                  'valid': False,
                  'end': False,
                  'next': False,
                  'bottom': False,
                  }

        if command == 'delete':
            result['score'] = self.deleteRows()
            result['end'] = not self.getNextBlock()
            result['next'] = True
            curses.beep()
            return result

        self.removeBlock()

        newCoordinates = list(self.coordinates)
        newBlock = self.currentBlock

        result['cells'] = self.currentBlock.listBody(newCoordinates)

        if command in Board.MOVEMENTS:
            newCoordinates = self.changeCoordinates(command, newCoordinates)

        elif command == Board.ROTATE:
            newBlock = self.currentBlock.rotate()

        if self.placeBlock(newBlock, newCoordinates):

            # The Block Can Be Placed At The New Spot #

            self.coordinates = newCoordinates
            self.currentBlock = newBlock
            if command == curses.KEY_DOWN:
                result['valid'] = True

            # See if Block is At Bottom #

            self.removeBlock()
            testCoordinates = self.changeCoordinates(curses.KEY_DOWN, list(self.coordinates))
            if not self.canPlaceBlock(self.currentBlock, testCoordinates):
                # curses.flash()
                result['bottom'] = True
            self.placeCurrentBlock()

        else:
            if command == curses.KEY_DOWN:

                # The Block Cannot Go Down Any Further #

                self.placeBlock(self.currentBlock, self.coordinates)

                if self.extraTime and self.hasExtraTime:

                    # Allow Double Time for Repositioning At Higher Speeds #

                    curses.flash()
                    self.hasExtraTime = False
                    result['valid'] = True

                else:
                    if self.extraTime:
                        self.hasExtraTime = True
                    self.findRowsToClear()
                    result['clear'] = self.rowsToClear
                    result['valid'] = True
                    if self.rowsToClear == []:
                        result['next'] = True
                        result['end'] = not self.getNextBlock()
            else:

                # Block Cannot Be Moved Left/Right or Rotate

                self.placeBlock(self.currentBlock, self.coordinates)

        result['cells'].extend(self.currentBlock.listBody(self.coordinates))
        return result

    def changeCoordinates(self, command, coordinates):
        if command == curses.KEY_DOWN:
            coordinates[1] -= 1
        elif command == curses.KEY_LEFT:
            coordinates[0] -= 1
        elif command == curses.KEY_RIGHT:
            coordinates[0] += 1
        return coordinates

    def canPlaceBlock(self, block, coordinates):
        for body in block.body:
            x = coordinates[0] + body[0]
            if x < 0 or x >= self.length:
                return False

            y = coordinates[1] + body[1]
            if y < 0 or y >= self.height + 2 or (y >= self.height and (x < 2 or x > 6)):
                return False

            if self.board[y][x] != ' ':
                return False

        return True

    def placeBlock(self, block, coordinates):
        canPlace = self.canPlaceBlock(block, coordinates)

        if canPlace:
            for body in block.body:
                self.board[coordinates[1] + body[1]][coordinates[0] + body[0]] = block.type
            return True

        else:
            return False

    def placeCurrentBlock(self):
        for body in self.currentBlock.body:
            self.board[self.coordinates[1] + body[1]][self.coordinates[0] + body[0]] = self.currentBlock.type

    def moveBlocks(self):
        for i in range(2):
            self.nextGrid[i] = [' '] * 9
            self.afterGrid[i] = [' '] * 9

        for body in self.nextBlock.body:
            self.nextGrid[Board.NEXT_ORIGIN[1] + body[1]][Board.NEXT_ORIGIN[0] + body[0]] = self.nextBlock.type
        for body in self.afterBlock.body:
            self.afterGrid[Board.NEXT_ORIGIN[1] + body[1]][Board.NEXT_ORIGIN[0] + body[0]] = self.afterBlock.type

    def findRowsToClear(self):
        self.rowsToClear = []

        for i, row in enumerate(self.board):
            for item in row:
                if item == ' ':
                    break
            else:
                self.rowsToClear.append(i)

        if self.rowsToClear == []:
            return False
        return True

    def deleteRows(self):
        score = len(self.rowsToClear)

        for row in sorted(self.rowsToClear, reverse=True):
            del self.board[row]
            self.board.insert(19, [' '] * self.length)

        self.rowsToClear = []
        return score

    def removeBlock(self):
        for body in self.currentBlock.body:
            self.board[self.coordinates[1] + body[1]][self.coordinates[0] + body[0]] = ' '

    def getNextBlock(self):
        self.currentBlock = self.nextBlock
        self.nextBlock = self.afterBlock
        self.afterBlock = Block()
        self.moveBlocks()
        self.coordinates = list(Board.ORIGIN)
        if self.board[20] != ['X', 'X', ' ', ' ', ' ', ' ', ' ', 'X', 'X', 'X'] and \
           self.board[21] != ['X', 'X', ' ', ' ', ' ', ' ', ' ', 'X', 'X', 'X']:
            return False
        if not self.placeBlock(self.currentBlock, self.coordinates):
            return False
        return True

    def getCell(self, coordinates, board):
        if board == 0:
            return self.board[coordinates[1]][coordinates[0]]
        elif board == 1:
            return self.nextGrid[coordinates[1]][coordinates[0]]
        elif board == 2:
            return self.afterGrid[coordinates[1]][coordinates[0]]

    def enableExtraDropTime(self):
        self.extraTime = True
        self.hasExtraTime = True

    def disableExtraDropTime(self):
        self.extraTime = False
        self.hasExtraTime = False
