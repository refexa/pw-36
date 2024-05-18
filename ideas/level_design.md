# Level Design

### Game

- Game is a seven levels of progressive difficulty
- (Details of game levels...)
- (Win game condition?)
- (Lose game condition?)


### Level

- Level is larger than the screen
- Level is typically multiple screen-size segments arrange in a straight line
- Level has a Start and Finish, permanent walls, a Ship, and various destructible enemies
- Game camera scrolls from Start to Finish
- Level has in invisible bounding box to keep Ship positioned on the screen; this box moves in sync with the camera
- Events may trigger during travel from Start to Finish
- Level is won when Ship reaches Finish and meets the requirements to move on
- Level is lost when Ship is destroyed


### Bounding Box

#### Metrics

- Box is smaller than the screen
- Box is roughly centered on the screen (TBD)

#### Movement

- Ship cannot move outside this box
- Box is moved in a straight line from Start to Finish within the level

#### Interaction

- Box forces Ship to stay within its bounds


### Ship

- Ship is the player's avatar

#### Movement

- Ship can move in any direction
- If Ship is not moved by player, Box will force Ship forward as it moves

#### Interaction

- Ship has a weapon that fires projectiles
- Ship projectiles fires in (which direction(s))
- Ship shields take damage when colliding with enemies, including enemy projectiles
- Ship shield damage is measured in Dark Matter units
- When Ship shields run out, any damage destroys Ship
- Using Ship weapon decrements Dark Matter


### Enemies

- (To be documented..)
