# README #

Refexa has also published it on Github.

## Dark matter keeper - Pyweek 36 ##

* Pyweek 36
* Theme: Dark Matter
* [Multifac's project on pyweek.org](https://pyweek.org/e/GD-36/)
* Team members (pyweek.org names): DR0ID, gummbum, tabishrfx, PyNon

### How do I get set up? ###

* Download the final package, unpack the files into a dedicated directory
* No configuration is necessary
* Install dependencies:
  * Install Python 3.10+
  * In the game directory: pip install -r requirements.txt
  * Dependencies: Python 3.10+, pygame-ce 2.3.2 or pygame 2.5.2 (developed and tested with these; other versions may work, but please do not report bugs with other versions)
* Run the game in Python 3.10+:
  * python run_game.py
  * py3 run_game.py
  * py -3 run_game.py

### Who do I talk to? ###

* @dr0id_ in Python#pyweek-game-jam
* @.mrgumm in Python#pyweek-game-jam

### How to play the game ###

In a universe powered by DARK MATTER...

Welcome to another bullet hell.

You are a grizzled space marine. Thought you could retire, eh? Well, no profit brooding over this dark matter. Once a
grizzled space marine always a grizzled space marine. Embrace the suck, as they say. Separated from your fighter squad
during a dangerous mission, you must get out of enemy territory with all your assets still intact. Against overwhelming
odds - naturally - wherever you find yourself, make it to the exit portal. May you live to boast about it beside the
quaint retro diesel fire back at the cantina. We would disavow all knowledge, but what's the point? One glance makes
it obvious...you're Marine. Move out

In the game's startup menu find controls to adjust the music and sound volume, and switch between mouse and keyboard
controls. Mouse is recommended.

Play the first level with a little patience. It only costs you a minute to observe what's going on. Press "r" to restart
the level if you want to get a better feel for the controls and gui. Note there is an energy bank labeled DARK MATTER,
and an energy bank for your ship's shield.

* The shield is depleted when the ship collides with dangers in the area.
* DARK MATTER is depleted by shield regeneration, and by firing the ship's directed energy weapon.

Pick up more DARK MATTER from blue bottles laying about. The enemy was nice enough to collect them, you may as well help
yourself to them.

Avoid red bottles. These are mines cleverly disguised as DARK MATTER containers, but they drain large amounts of DARK
MATTER.

And of course, avoid the swarms of enemy ships and directed energy weapons.

Do not be shy. Victory favors the bold.

### Tips ###

If your rig can't keep up with the CPU load, type the digits "32" while in your ship to toggle off the star field.

If you're having trouble with a level you can restart with "r", or skip ahead with "k".

There are loads of debugging features Sarge never told you about. You might enjoy some of his secret toys. Look in the
"featureswitches.py" manual.

If you want to report a bug and try to determine the steps to reproduce it, you can jump directly to a level by
creating game/_custom.py, and putting in it commands similar to the following:

class Settings:
    initial_level = 4

Then start the game and exercise the devil out of that level.

If you say bad words during gameplay, don't put any money in the jar. There isn't enough money in the multiverse to
pay it off. Enjoy the freebie. :)

### Thanks ###

Thank you for playing. And if you made a game for Pyweek 36, thank you and good luck.
