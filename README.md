# cycles

Cycles is a game where one or two human players compete with each other or multiple AI to be the last standing in a shrinking arena. There are two 1v1 modes and two 6p free-for-all modes of play.

It is written in Python and uses the Pygame library. The font used is DejaVu Sans Mono.

Players move around the open area. You crash if you hit a trail, an obstacle or the arena edges. You score by surviving the longest time. Some obstacles are randomly placed around every round.

Every 20 seconds, the open area shrinks. This makes it harder to manuveur in a smaller and smaller space.

Controls:
- WASD (player 1) and arrows (player 2) for movement
- ESC will give you a prompt to exit game or start new round
- P is pause/unpause

Have fun!


## How to run:

To run the game script, you will need to have Python 3 installed.
You will also need to install pygame: `pip install pygame`

Then you can just navigate to the game directory and run it with `python cycles.py`

Note you may need to substitute python to python3 or pip to pip3 depending on what OS or distro you use.
Virtual environment recommended if you are familiar with those.

If you are on Windows, you can just go to the releases section and grab the Windows release zip file.
Then, extract the folder somewhere. Inside it you will find cycles.exe and just run it. No Python or Pygame needed
for this, works out of the box.

## Extra - how to build executable:

To build an executable file, you will need Pygame as stated above. In addition to that, you will also need
to install cx_Freeze: `pip install cx_Freeze`

Then just navigate to the game dir, and run `python setup.py build`. After this, a new 'build' dir will be created
and there you will find the necessary files.
