# Tetris
Recreation of the classic Tetris game with text-based graphics. 
Created during my Junior year at DePaul university, my goals with this project was to experiment with the curses module
and threading to create a text-based non turn-based game that deals with user-input concurrently with computer input. 

## Getting Started
__Language Version:__ Python 3.5

__Usage:__
```
$ python3 main.py <starting_speed_level>
```

__It is recommended to run Tetris in a Terminal using 15pt Andale Mono font to ensure proper spacing.__

The Tetris repository includes the following python modules:
* main.py
* block.py
* board.py
* game.py

Tetris does not require the download of any third-party modules and only uses standard Python library modules.

## How To Play
### Point Values
Each value is multiplied by the current speed level.
* _Placing Block_ = 15 points
* _Single_ = 200 points
* _Double_ = 600 points
* _Triple_ = 1500 points
* _Tetris_ = 2500 points

### Controls
* __left/right arrow -__ Move block left and right
* __down arrow__ - Move block down
* __space bar__ - Rotate block
* __d__ - Drop block to the bottom
* __p -__ Pause game
* __q -__ Quit game