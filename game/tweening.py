# -*- coding: utf-8 -*-

"""
Tweening
========

Tweening is about ease functions. These ease functions facilitate to interpolate a value between a and b in different
ways in a certain time. The ease functions are often used to move an object in a visually pleasant way. Instead of
moving an object from a to b in a linear movement in a certain time, another ease function can be used that starts
moving the object fast and slows down when approaching target position b.


So how is this all implemented?
There are many predefined ease functions (see the demo, just run this file a a script or look through the code). The
interface of such a ease functions is always the same:

.. code:: python

    def ease_xy(t, b, c, d, p)

    # t is the current *t*ime of the tween that is calculated.
    # b is the *b*egin value
    # c is the *c*hange value
    # d is the *d*uration, how long it will take until the target b + c is reached
    # p are the *p*arameters used by some ease functions that can be parametrized, see descriptions for details

With such a function one could do easing already, but would be cumbersome because all the values have to be managed.
Therefore the :py:class:`Tweener` class has been introduced. It manages the life cycle and updating of the
:py:class:`_Tween`
objects. The reason is to have just one update method instead of many (one on each tween). This has also the nice
side effect to save some performance since a method call in python is not that cheap. In this way all tweens
created by this instance of a tweener can be updated efficiently.

The tweening works by calling a ease function that calculates the value corresponding to the time passed. This value
is then set to the defined attribute of an object.

To make the tweening even more useful a callback can be passed that is called when the tween has ended. This can be
used to chain multiple tweens in a sequence and move an object in interesting ways around by combining different
ease functions. Or other things can be triggered by this callback of course.



Example:

In a platformer game there is always a moving platform. Typically such a platform is moving forth and back. This
movement can be implemented in a very simple way using a tween (well actually using two tweens). Assume such
a moving platform p has to move between the coordinates 200 and 250 in 3 seconds. So p.x should be set
initially to 200. Using the tweener this would look like this:

.. code:: python

    p = Platform()
    tweener = Tweener()
    tween = tweener.create_tween(p, "x", 200, 50, 3)  # linear movement between 200 to 250 in 3 seconds

But wait, this is only half of the way. Once the platform has reached the far end, it should return. One solution
is to add a callback that creates another tween that moves the platform back.


.. code:: python

    def move_forth(tween, tweener):
        tweener.create_tween(tween.o, tween.a, 200, 50, 3, cb_end=move_back, cb_args=[tweener])

    def move_back(tween, tweener):
        tweener.create_tween(tween.o, tween.a, 250, -50, 3, cb_end=move_forth, cb_args=[tweener])

    tween = tweener.create_tween(p, "x", 200, 50, 3, cb_end=move_back, cb_args=[tweener])

    while 1:
        ...
        tweener.update(dt)
        ...


With this setup the platform would move forth and back as long tweener.update(dt) is called. The trick here is
that the move_forth() callback creates a tween that calls move_back() at the end. Then a new tween is created
that calls move_forth() again at the end and so on.

There are some more features implemented. Take a look at the create_tween doc string.


There are also nested groups of serial and parallel execution of tweens. The
groups can be nested and repeated.

Following methods have been added to the Tween class:

::

    next(*others)
    parallel(*others)
    repeat(n)

This methods allow the creation of complex, nested constructs that can be executed in a simple way. This
should simplify the handling of multiple tweens and their callbacks and their execution.

.. code:: python

    tweener = Tweener()

    car = MyCar()
    duration = 60  # seconds
    # create tweens that manipulate an attribute of the car
    tween1 = tweener.create_tween(car, 'x', 0, 100, duration, do_start=False)
    tween2 = tweener.create_tween(car, 'y', 0, 100, duration, do_start=False)
    tween3 = tweener.create_tween(car, 'z', 0, 100, duration, do_start=False)
    tween4 = tweener.create_tween(car, 'a', 0, 100, duration, do_start=False)
    tween5 = tweener.create_tween(car, 'v', 0, 100, duration, do_start=False)

    serial = tween1.next(tween2)

    parallel = tween3.parallel(tween4)

    repeated = tween5.repeat(3)

    # nested
    nested1 = serial.parallel(parallel)
    nested2 = serial.next(parallel)

    # or even
    nested3 = nested1.parallel(nested2).repeat(2)

    # don't forget to start, otherwise nothing will happen
    nested3.start()


Have fun using tweening!


This code and equations are based on:

http://wiki.python-ogre.org/index.php?title=CodeSnippits_pyTweener
http://hosted.zeh.com.br/tweener/docs/en-us/misc/transitions.html
http://code.google.com/p/tweener/source/browse/trunk/as3/caurina/transitions/Equations.as

Design of the tweens is based on:

http://www.robertpenner.com/easing/penner_chapter7_tweening.pdf

"""
from __future__ import print_function, division

import logging
import random
from math import asin
from math import cos
from math import isnan
# noinspection PyPep8Naming
from math import pi as PI
from math import pow
from math import sin
from math import sqrt

logger = logging.getLogger(__name__)
logger.debug("importing...")

__version__ = '2.0.1.0'

__author__ = "DR0ID"
__email__ = "dr0iddr0id {at} gmail [dot] com"
__copyright__ = "DR0ID @ 2022"
__credits__ = ["DR0ID"]  # list of contributors
__maintainer__ = "DR0ID"
__license__ = "New BSD license"

# for easy comparison as in sys.version_info but digits only
__version_info__ = tuple([int(_d) for _d in __version__.split('.')])

TWO_PI = PI * 2
HALF_PI = PI / 2.0


#  noinspection PyUnusedLocal
def ease_linear(t, b, c, d, p):  # pragma: nocover
    return c * t / d + b


# noinspection PyUnusedLocal
def ease_in_quad(t, b, c, d, p):  # pragma: nocover
    t /= d
    return c * t * t + b


# noinspection PyUnusedLocal
def ease_out_quad(t, b, c, d, p):  # pragma: nocover
    t /= d
    return -c * t * (t - 2) + b


# noinspection PyUnusedLocal
def ease_in_out_quad(t, b, c, d, p):  # pragma: nocover
    t /= d / 2.0
    if t < 1:
        return c / 2.0 * t * t + b
    t -= 1
    return -c / 2.0 * (t * (t - 2) - 1) + b


def ease_out_in_quad(t, b, c, d, p):  # pragma: nocover
    if t < d / 2:
        return ease_out_quad(t * 2, b, c / 2, d, p)
    return ease_in_quad((t * 2) - d, b + c / 2, c / 2, d, p)


# noinspection PyUnusedLocal
def ease_in_cubic(t, b, c, d, p):  # pragma: nocover
    t /= d
    return c * t * t * t + b


# noinspection PyUnusedLocal
def ease_out_cubic(t, b, c, d, p):  # pragma: nocover
    t = t / d - 1
    return c * (t * t * t + 1) + b


# noinspection PyUnusedLocal
def ease_in_out_cubic(t, b, c, d, p):  # pragma: nocover
    t /= d / 2
    if t < 1:
        return c / 2 * t * t * t + b
    t -= 2
    return c / 2 * (t * t * t + 2) + b


# noinspection PyUnusedLocal
def ease_out_in_cubic(t, b, c, d, p):  # pragma: nocover
    if t < d / 2:
        return ease_out_cubic(t * 2, b, c / 2, d, p)
    return ease_in_cubic((t * 2) - d, b + c / 2, c / 2, d, p)


# noinspection PyUnusedLocal
def ease_in_quart(t, b, c, d, p):  # pragma: nocover
    t /= d
    return c * t * t * t * t + b


# noinspection PyUnusedLocal
def ease_out_quart(t, b, c, d, p):  # pragma: nocover
    t = t / d - 1
    return -c * (t * t * t * t - 1) + b


# noinspection PyUnusedLocal
def ease_in_out_quart(t, b, c, d, p):  # pragma: nocover
    t /= d / 2
    if t < 1:
        return c / 2 * t * t * t * t + b
    t -= 2
    return -c / 2 * (t * t * t * t - 2) + b


def ease_out_in_quart(t, b, c, d, p):  # pragma: nocover
    if t < d / 2:
        return ease_out_quart(t * 2.0, b, c / 2, d, p)
    return ease_in_quart((t * 2) - d, b + c / 2, c / 2, d, p)


# noinspection PyUnusedLocal
def ease_in_quint(t, b, c, d, p):  # pragma: nocover
    t = t / d
    return c * t * t * t * t * t + b


# noinspection PyUnusedLocal
def ease_out_quint(t, b, c, d, p):  # pragma: nocover
    t = t / d - 1
    return c * (t * t * t * t * t + 1) + b


# noinspection PyUnusedLocal
def ease_in_out_quint(t, b, c, d, p):  # pragma: nocover
    t /= d / 2
    if t < 1:
        return c / 2 * t * t * t * t * t + b
    t -= 2
    return c / 2 * (t * t * t * t * t + 2) + b


# noinspection PyUnusedLocal
def ease_out_in_quint(t, b, c, d, p):  # pragma: nocover
    c /= 2
    if t < d / 2:
        return ease_out_quint(t * 2, b, c, d, p)
    return ease_in_quint(t * 2 - d, b + c, c, d, p)


# noinspection PyUnusedLocal
def ease_in_sine(t, b, c, d, p):  # pragma: nocover
    return -c * cos(t / d * HALF_PI) + c + b


# noinspection PyUnusedLocal
def ease_in_sine2(t, b, c, d, p):  # pragma: nocover
    return c * cos(t / d * TWO_PI) + b


# noinspection PyUnusedLocal
def ease_in_sine3(t, b, c, d, p):  # pragma: nocover
    return c * sin(t / d * TWO_PI) + b


# noinspection PyUnusedLocal
def ease_out_sine(t, b, c, d, p):  # pragma: nocover
    return c * sin(t / d * HALF_PI) + b


# noinspection PyUnusedLocal
def ease_in_out_sine(t, b, c, d, p):  # pragma: nocover
    return -c / 2 * (cos(PI * t / d) - 1) + b


def ease_out_in_sine(t, b, c, d, p):  # pragma: nocover
    if t < d / 2:
        return ease_out_sine(t * 2, b, c / 2, d, p)
    return ease_in_sine((t * 2) - d, b + c / 2, c / 2, d, p)


# noinspection PyUnusedLocal
def ease_in_circ(t, b, c, d, p):  # pragma: nocover
    t /= d + 0.0005
    return -c * (sqrt(1 - t * t) - 1) + b


# noinspection PyUnusedLocal
def ease_out_circ(t, b, c, d, p):  # pragma: nocover
    t = t / d - 1
    return c * sqrt(1 - t * t) + b


# noinspection PyUnusedLocal
def ease_in_out_circ(t, b, c, d, p):  # pragma: nocover
    t /= d / 2
    if t < 1:
        return -c / 2 * (sqrt(1 - t * t) - 1) + b
    t -= 2
    return c / 2 * (sqrt(1 - t * t) + 1) + b


# noinspection PyUnusedLocal
def ease_out_in_circ(t, b, c, d, p):  # pragma: nocover
    if t < d / 2:
        return ease_out_circ(t * 2, b, c / 2, d, p)
    return ease_in_circ(t * 2 - d, b + c / 2, c / 2, d, p)


# noinspection PyUnusedLocal
def ease_in_expo(t, b, c, d, p):  # pragma: nocover
    return b if t == 0 else c * (2 ** (10 * (t / d - 1))) + b - c * 0.001


# noinspection PyUnusedLocal
def ease_out_expo(t, b, c, d, p):  # pragma: nocover
    return b + c if (t == d) else c * (-2 ** (-10 * t / d) + 1) + b


# noinspection PyUnusedLocal
def ease_in_out_expo(t, b, c, d, p):  # pragma: nocover
    if t == 0:
        return b
    if t == d:
        return b + c
    t /= d / 2
    if t < 1:
        return c / 2 * pow(2, 10 * (t - 1)) + b - c * 0.0005
    return c / 2 * 1.0005 * (-pow(2, -10 * (t - 1)) + 2) + b


# noinspection PyUnusedLocal
def ease_out_in_expo(t, b, c, d, p):  # pragma: nocover
    if t < d / 2:
        return ease_out_expo(t * 2, b, c / 2, d, p)
    return ease_in_expo((t * 2) - d, b + c / 2, c / 2, d, p)


# noinspection PyUnusedLocal
def ease_in_elastic(t, b, c, d, params):  # pragma: nocover
    if t == 0:
        return b
    t /= d
    if t == 1:
        return b + c
    p = d * 0.3 if params is None or isnan(params.period) else params.period
    a = 0 if params is None or isnan(params.amplitude) else params.amplitude
    if a == 0 or a < abs(c):
        a = c
        s = p / 4
    else:
        s = p / TWO_PI * asin(c / a)
    t -= 1
    return -(a * pow(2, 10 * t) * sin((t * d - s) * TWO_PI / p)) + b


# noinspection PyUnusedLocal
def ease_out_elastic(t, b, c, d, params):  # pragma: nocover
    if t == 0:
        return b
    t /= d
    if t == 1:
        return b + c
    p = d * 0.3 if params is None or isnan(params.period) else params.period
    a = 1.0 if params is None or isnan(params.amplitude) else params.amplitude
    if a == 0 or a < abs(c):
        a = c
        s = p / 4
    else:
        s = p / TWO_PI * asin(c / a)

    return a * pow(2, -10 * t) * sin((t * d - s) * TWO_PI / p) + c + b


def ease_in_out_elastic(t, b, c, d, params):  # pragma: nocover
    if t == 0:
        return b
    t /= d / 2
    if t == 2:
        return b + c
    p = d * 0.3 * 1.5 if params is None or isnan(params.period) else params.period
    a = 0 if params is None or isnan(params.amplitude) else params.amplitude
    if a == 0 or a < abs(c):
        a = c
        s = p / 4
    else:
        s = p / TWO_PI * asin(c / a)
    if t < 1:
        t -= 1
        return -0.5 * (a * pow(2, 10 * t) * sin((t * d - s) * TWO_PI / p)) + b
    t -= 1
    return a * pow(2, -10 * t) * sin((t * d - s) * TWO_PI / p) * 0.5 + c + b


def ease_out_in_elastic(t, b, c, d, p):  # pragma: nocover
    if t < d / 2:
        return ease_out_elastic(t * 2, b, c / 2, d, p)
    return ease_in_elastic((t * 2) - d, b + c / 2, c / 2, d, p)


def ease_in_back(t, b, c, d, p):  # pragma: nocover
    s = 1.70158 if p is None or isnan(p.overshoot) else p.overshoot
    t /= d
    return c * t * t * ((s + 1) * t - s) + b


def ease_out_back(t, b, c, d, p):  # pragma: nocover
    s = 1.70158 if p is None or isnan(p.overshoot) else p.overshoot
    t = t / d - 1
    return c * (t * t * ((s + 1) * t + s) + 1) + b


def ease_in_out_back(t, b, c, d, p):  # pragma: nocover
    s = 1.70158 if p is None or isnan(p.overshoot) else p.overshoot
    t /= d / 2
    if t < 1:
        s *= 1.525
        return c / 2 * (t * t * ((s + 1) * t - s)) + b
    s *= 1.525
    t -= 2
    return c / 2 * (t * t * ((s + 1) * t + s) + 2) + b


def ease_out_in_back(t, b, c, d, p):  # pragma: nocover
    if t < d / 2:
        return ease_out_back(t * 2, b, c / 2, d, p)
    return ease_in_back((t * 2) - d, b + c / 2, c / 2, d, p)


# noinspection PyUnusedLocal
def ease_in_bounce(t, b, c, d, p=None):  # pragma: nocover
    return c - ease_out_bounce(d - t, 0, c, d) + b


# noinspection PyUnusedLocal
def ease_out_bounce(t, b, c, d, p=None):  # pragma: nocover
    t /= d
    if t < (1 / 2.75):
        return c * (7.5625 * t * t) + b
    elif t < (2 / 2.75):
        t -= (1.5 / 2.75)
        return c * (7.5625 * t * t + 0.75) + b
    elif t < (2.5 / 2.75):
        t -= (2.25 / 2.75)
        return c * (7.5625 * t * t + 0.9375) + b
    else:
        t -= (2.625 / 2.75)
        return c * (7.5625 * t * t + 0.984375) + b


# noinspection PyUnusedLocal
def ease_in_out_bounce(t, b, c, d, p):  # pragma: nocover
    if t < d / 2:
        return ease_in_bounce(t * 2, 0, c, d) * 0.5 + b
    else:
        return ease_out_bounce(t * 2 - d, 0, c, d) * 0.5 + c * 0.5 + b


def ease_out_in_bounce(t, b, c, d, p):  # pragma: nocover
    if t < d / 2:
        return ease_out_bounce(t * 2, b, c / 2, d, p)
    return ease_in_bounce((t * 2) - d, b + c / 2, c / 2, d, p)


def ease_random_int_bounce(t, b, c, d, p=(0, 1)):  # pragma: nocover
    """
    Random bouncing in range provided in p.

    :param t: current time
    :param b: begin
    :param c: change
    :param d: duration
    :param p: (x, y) tuple defining random range [x, y]
    :return: for t==0 returns b, random value in range [x, y] for t < d, otherwise b + c
    """
    if t < d:
        if t == 0:
            return b
        p = (0, 1) if p is None else p
        return b + random.randint(*p)
    else:
        return b + c


class Parameters(object):
    """
    The parameters for the ease functions.

    :param period: default is nan, the period of the function
    :param amplitude: default is nan, the amplitude of the function
    :param overshoot: default is nan, the overshoot of the function
    """

    def __init__(self, period=float("nan"), amplitude=float("nan"), overshoot=float("nan")):
        self.period = float(period)
        self.amplitude = float(amplitude)
        self.overshoot = float(overshoot)


class TweenStates(object):
    error = 0
    created = 1
    active = 2
    paused = 3
    ended = 4


class UnknownTweenStateException(Exception):
    """Exception raised when a unknown state is provided."""

    def __init__(self, state):
        """
        The unknown TweenState exception.
        :param state: The unknown state to report.
        """
        msg = "Unknown state '{0}'! Should be one from Tweener.TweenState.".format(state)
        Exception.__init__(self, msg)


class TweenNotInAppropriateStateException(Exception):
    """Exception to indicate that a tween is not in the expected state."""
    pass


class TweenBelongsToOtherTweenerException(Exception):
    pass


TweenStateNames = {
    TweenStates.error: "error",
    TweenStates.active: "active",
    TweenStates.paused: "paused",
    TweenStates.ended: "ended",
    TweenStates.created: "created",
    "error": TweenStates.error,
    "active": TweenStates.active,
    "paused": TweenStates.paused,
    "ended": TweenStates.ended,
    "created": TweenStates.created,
}
"""
The conversion dictionary between string description and state values e.g.
   TweenStateNames["active"] -> Tweener.TweenStates.active
   TweenStateNames[Tweener.TweenStates.active] -> "active"
"""


class _Parallel(object):
    """The group for parallel tween execution control.

    .. code:: python

        tweener = tweening.Tweener(...)
        tween1 = tweener.crate_tween(...)
        tween2 = tweener.crate_tween(...)
        parallel_group = _Parallel(tweener, tween1, tween2)

        # execute
        parallel_group.start()
    """

    def __init__(self, tweener, *tweens):
        """
        Parallel group execution control constructor.
        :param tweener: The tweener instance to use. Has to be the same in all instances.
        :param tweens: The tweens or groups to execute in parallel.
        """
        self._tween_callbacks = {}
        self.tweener = tweener
        self._tweens = list(tweens)
        self.state = tweener.TweenStates.created
        self._validate_tweens_state_and_same_tweener()
        self.cb = None
        self.cb_args = tuple()
        self.t = 0
        self._current_tween_cb = None
        self.__max_dur_tween = None

    def _validate_tweens_state_and_same_tweener(self):
        for t in self._tweens:
            if t.tweener != self.tweener:
                raise TweenBelongsToOtherTweenerException()
            if t.state != TweenStates.created:
                raise TweenNotInAppropriateStateException()

    @property
    def count(self):
        """Returns the item count contained in this group."""
        return len(self._tweens)

    @property
    def d(self):
        """Returns the duration of the longest tween (which defines the duration of the group)."""
        return list(sorted(self._tweens, key=lambda t: t.d))[-1].d

    def next(self, *other):
        """
        Schedules the next tweens for serial execution.
        :param other: the tweens or groups to execute
        :return: a serial group
        """
        return _Serial(self.tweener, self, *other)

    def parallel(self, *other):
        """
        Schedules the next tweens for parallel execution.
        :param other: the tweens or groups to execute
        :return: a parallel group
        """
        return _Parallel(self.tweener, self, *other)

    def repeat(self, count):
        """
        Repeat the entire group n times.
        :param count: how many times it will be repeated. If set to < 1 then it will loop endless.
        :return: a serial group containing itself n times.
        """
        if count < 1:
            s = _Serial(self.tweener, self)
            s.is_looping = True
            return s

        repeated = [self] * count
        return _Serial(self.tweener, *repeated)

    def pause(self):
        """Pause the tween execution of all contained tweens."""
        self.state = TweenStates.paused
        for _t in self._tweens:
            _t.pause()

    def resume(self):
        """Resume the tween execution."""
        self.state = TweenStates.active
        for _t in self._tweens:
            _t.resume()

    def start(self, immediate=True):
        """
        Start the tween execution.
        :param immediate: if true, calculates the first value of the tweens when start is called, defaults to False
        """
        self.t = 0
        self._tween_callbacks.clear()
        for _t in self._tweens:
            _t.start(immediate=immediate)
            self._tween_callbacks[_t] = _t.cb
            _t.cb = self.call_back_to_parallel

        self.state = TweenStates.active

    def stop(self):
        """Stop all tween execution of all contained tweens."""
        self.state = TweenStates.ended
        for _t in self._tweens:
            _t.stop()
            if _t in self._tween_callbacks:
                _t.cb = self._tween_callbacks[_t]
        self._tween_callbacks.clear()

    def call_back_to_parallel(self, *args):
        """
        The call back used internally to track tween execution state.
        :param args: any args passed by the caller of the callback
        """
        # this is only called from the max duration tween
        ended_tween = args[-1]

        self.t = ended_tween.t  # this is automatically the longest running tween time (because called last)

        ended_tween.cb = self._tween_callbacks.pop(ended_tween, None)
        if ended_tween.cb is not None:
            ended_tween.cb(*(list(ended_tween.cb_args) + [ended_tween]))

        if self.cb and len(self._tween_callbacks) == 0:
            self.cb(*(list(self.cb_args) + [self]))


class _Serial(object):
    """The group for serial tween execution control.

    .. code:: python

        tweener = tweening.Tweener(...)
        tween1 = tweener.crate_tween(...)
        tween2 = tweener.crate_tween(...)
        serial_group = _Serial(tweener, tween1, tween2)

        # execute
        serial_group.start()
    """

    def __init__(self, tweener, *tweens):
        """
        Serial group execution control constructor.
        :param tweener: The tweener instance to use. Has to be the same in all instances.
        :param tweens: The tween or groups to execute in series.
        """
        self._tweens = list(tweens)
        self.tweener = tweener
        self.state = TweenStates.created
        self.cb = None
        self.cb_args = tuple()
        self._current_tween_index = -1
        self._validate_tweens_state_and_same_tweener()
        self.immediate = False
        self._current_tween_cb = None
        self.t = 0
        self.is_looping = False

    def _validate_tweens_state_and_same_tweener(self):
        for t in self._tweens:
            if t.tweener != self.tweener:
                raise TweenBelongsToOtherTweenerException()
            if t.state != TweenStates.created:
                msg = "Should be 'created' but is '{0}' " \
                      "(hint: forgot about do_start=False?)".format(TweenStateNames[t.state])
                raise TweenNotInAppropriateStateException(msg)

    @property
    def count(self):
        """Returns the item count contained in this group."""
        return len(self._tweens)

    @property
    def d(self):
        """Returns the sum of durations of all tweens."""
        return sum(_t.d for _t in self._tweens)

    def next(self, *other):
        """
        Schedules the next tweens for serial execution.
        :param other: the tweens or groups to execute
        :return: a serial group
        """
        return _Serial(self.tweener, self, *other)

    def parallel(self, *other):
        """
        Schedules the next tweens for parallel execution.
        :param other: the tweens or groups to execute
        :return: a parallel group
        """
        return _Parallel(self.tweener, self, *other)

    def repeat(self, count):
        """
        Repeat the entire group n times.
        :param count: how many times it will be repeated. If set to < 1 then it will loop endless.
        :return: a serial group containing itself n times.
        """
        if count < 1:
            s = _Serial(self.tweener, self)
            s.is_looping = True
            return s

        repeated = [self] * count
        return _Serial(self.tweener, *repeated)

    def pause(self):
        """Pause the tween execution of all contained tweens."""
        self.state = TweenStates.paused
        self._tweens[self._current_tween_index].pause()

    def resume(self):
        """Resume the tween execution."""
        self.state = TweenStates.active
        self._tweens[self._current_tween_index].resume()

    def start(self, immediate=True):
        """
        Start the tween execution.
        :param immediate: if true, calculates the first value of the tweens when start is called, defaults to False
        """
        self.stop()
        self._current_tween_index = -1
        self.immediate = immediate
        self.t = 0
        self._start_tween()
        self.state = TweenStates.active

    def stop(self):
        """Stop all tween execution of all contained tweens."""
        for _t in self._tweens:
            _t.stop()
        if self.state == TweenStates.active:
            _current_tween = self._tweens[self._current_tween_index]
            _current_tween.cb = self._current_tween_cb
        self.state = TweenStates.ended

    def _start_tween(self, over_time=0):
        _tween = self._get_next_tween()
        if _tween is not None:
            self._current_tween_index += 1
            while _tween.d <= over_time:
                # call cb of tween
                if _tween.cb:
                    _tween.cb(*(list(_tween.cb_args) + [_tween]))

                # update attr of object
                setattr(_tween.o, _tween.a, _tween.f(_tween.d, _tween.b, _tween.c, _tween.d, _tween.p))

                # skip to next
                # over_time -= _tween.d
                _tween = self._get_next_tween()
                if _tween is None:
                    # no tween left in series
                    self._call_own_callback()
                    return
                else:
                    self._current_tween_index += 1

            self._current_tween_cb = _tween.cb
            _tween.cb = self.call_back_to_serial
            _tween.start(immediate=self.immediate)
            _tween.t += over_time  # set start time of tween to the actual time
        else:
            if self.is_looping:
                self._current_tween_index = -1
                self._start_tween(over_time)
            self._call_own_callback()

    def _call_own_callback(self):
        if self.cb:
            self.cb(*(list(self.cb_args) + [self]))

    def _get_next_tween(self):
        _next_tween_idx = self._current_tween_index + 1
        if _next_tween_idx >= len(self._tweens):
            return None
        return self._tweens[_next_tween_idx]

    def call_back_to_serial(self, *args):
        """
        The call back used internally to track tweens execution state.
        :param args: any args passed by the caller of the callback
        :return:
        """
        ended_tween = args[-1]
        over_time = ended_tween.t - ended_tween.d
        self.t += ended_tween.t
        ended_tween.cb = self._current_tween_cb
        if ended_tween.cb:
            ended_tween.cb(*(list(ended_tween.cb_args) + [ended_tween]))
        self._start_tween(over_time)


class _Tween(object):
    States = TweenStates

    def __init__(self, tweener, obj, attr_name, begin, change, duration, ease_function, params, delay, delta_update,
                 cb_end, *cb_args):
        assert duration > 0.0, "duration should be > 0.0"
        self.tweener = tweener  # the controlling Tweener instance
        self.o = obj
        self.a = attr_name
        self.cb = cb_end
        self.cb_args = cb_args
        self.state = self.States.created

        # tween variables
        self.delay = delay
        self.t = float(-delay)
        self.f = ease_function

        # tween parameters
        self.b = begin * 1.0  # convert to float
        self.c = change * 1.0  # convert to float
        self.d = float(duration)
        self.p = params

        # delta update
        self.v = self.b
        self.delta_update = delta_update

    def pause(self):
        self.tweener.pause_tween(self)

    def resume(self):
        self.tweener.resume_tween(self)

    def stop(self):
        self.tweener.remove_tween(self)

    def start(self, immediate=True):
        self.tweener.start_tween(self, immediate=immediate)

    def __str__(self):
        return "{0}<{1}, {2}, {3}>()".format(self.__class__.__name__, self.o, self.a, TweenStateNames[self.state])

    def parallel(self, *other):
        """
        Schedules itself and the other tweens or groups for parallel execution.
        :param other: the tweens or groups to execute
        :return: a parallel group
        """
        return _Parallel(self.tweener, self, *other)

    def next(self, *other):
        """
        Schedules the tweens or groups for serial execution.
        :param other: the tweens or groups to execute
        :return: a serial group
        """
        return _Serial(self.tweener, self, *other)

    def repeat(self, count):
        """
        Repeat the entire group n times.
        :param count: how many times it will be repeated. If set to < 1 then it will loop endless.
        :return: a serial group containing itself n times.
        """
        if count < 1:
            s = _Serial(self.tweener, self)
            s.is_looping = True
            return s

        repeats = [self] * count
        return _Serial(self.tweener, *repeats)


class Tweener(object):
    TweenStates = TweenStates

    def __init__(self, logger_instance=None):
        """
        The tweener class. It manages the life cycle of the tween (creation, update, remove).

        :param logger_instance: if set to None, then the default logger is used, if set to False no logging is done at
            all and if an instance is provided, then this one is used.
        """
        self._active_tweens = []  # ? maybe a dict? {entity: [tween]}
        self._paused_tweens = []
        self._logger = logger if logger_instance is None else (None if logger_instance is False else logger_instance)

    def update(self, delta_time):
        """
        The update method. It updates the tweens and calculates the new values of the tweens based on the time that
        has passed.

        :param delta_time: The time difference since last update.
        """
        ended_tweens = []
        for tween in self._active_tweens:
            tween.t += delta_time
            if tween.t >= 0.0:
                _cur_time = tween.t
                if tween.t >= tween.d:
                    ended_tweens.append(tween)
                    _cur_time = tween.d
                value = tween.f(_cur_time, tween.b, tween.c, tween.d, tween.p)
                if tween.delta_update:
                    delta = value - tween.v
                    tween.v = value
                    attr_value = getattr(tween.o, tween.a)
                    setattr(tween.o, tween.a, attr_value + delta)
                else:
                    setattr(tween.o, tween.a, value)
        for ended in ended_tweens:
            if self._logger:
                self._logger.debug("tween ended for obj: %s attr: %s", ended.o.__class__, ended.a)
            self._active_tweens.remove(ended)
            ended.state = self.TweenStates.ended
            if ended.cb is not None:
                args = list(ended.cb_args)
                args.append(ended)
                ended.cb(*args)

    # noinspection PyUnusedLocal,PyIncorrectDocstring
    def create_tween_by_end(self, obj, attr_name, begin, end, duration, ease_function=ease_linear, params=None,
                            cb_end=None, cb_args=tuple(), immediate=True, delay=0.0, delta_update=False,
                            do_start=True, *ignored_args):
        """
        Does the same thing as create_tween except that it takes a end instead of a change argument.


        :param end: What the end it should have in the given time.

        See create_tween for other params.
        """
        return self.create_tween(obj, attr_name, begin, end - begin, duration, ease_function, params, cb_end, cb_args,
                                 immediate, delay, delta_update, do_start, *ignored_args)

    # noinspection PyUnusedLocal
    def create_tween(self, obj, attr_name, begin, change, duration, ease_function=ease_linear, params=None,
                     cb_end=None, cb_args=tuple(), immediate=True, delay=0.0, delta_update=False, do_start=True,
                     *ignored_args):
        """
        This method is used create a tween.

        A tween has following attributes and methods:

            state current state for the tween (read only)
            States the available states (read only)

            def pause() -> None
                pauses this tween

            def resume() -> None
                resumes the tween

            def stop() -> None
                removes the tween from tweener

        There are some more attribute that really should only be used to look up value since they are used for the
        internal workings of the tween and tweener. These values correspond mostly the arguments of this method:

            o as the object it will manipulate
            a as the attribute name
            tweener as the tweener it was created

            cb as the end callback, might be None
            cb_args as the additional arguments for the end callback, might be an empty tuple

            t as the current time of the tween
            f as the reference to the used eas function

            b as the begin value
            c as the change value
            d as the duration value
            p as the parameters value, depends on the ease function

            delta_update is set to True when delta update is used, otherwise False
            v the value of the current step, only used if delta_update is set to True


        :param obj: The object to apply the ease function on.
        :param attr_name: The attribute of the object to apply the value.
        :param begin: The starting value.
        :param change: The amount of change it should cover in the given time. The end-value is determined as
            begin + change
        :param duration: The time it should take to reach the end value (begin + change) in seconds (actually it
            depends on the unit you use in the update method).
        :param ease_function: The ease function it should use. Default is :py:meth:`ease_linear`
        :param params: Some ease functions can be parametrized, see ease function description for details.
        :param cb_end: A callback when the tween has ended. Default is None. Last argument in `*args` is the ended tween
            instance.
        :param cb_args: The arguments to pass to the callback additionally to the tween itself, should be a
            list or tuple. Default is an empty tuple.
        :param delay: Delays the starting of the tween in seconds (actually it depends on the unit you use in
            the update method). Sometimes one wants to schedule multiple tween at once but let them start at
            different times. This delay does that. Default is 0.0
        :param immediate: If set to True, then the initial value is set directly after creation (even when delayed).
            Default is False.
        :param delta_update: Default is False. If set to True, then only the difference between the two update calls is
            added to the attribute on the object instead of setting the calculated value. This is interesting to move
            an object that does not have to be at a fixed point in space. Typically the begin value is set to 0 when
            using delta_updates. Using another value might give strange results.
        :param do_start: Starts the tween if set to True (default), otherwise either twee.start() or
            tweener.start_tween(tween) has to be used to start the tween.
        :param ignored_args: list of ignored args, its needed when using create_tween directly as callback.

        :return: a :py:class:`pyknic.tweening.Tweener._Tween` instance.
        """
        tween = _Tween(self, obj, attr_name, begin, change, duration, ease_function, params, delay, delta_update,
                       cb_end, *cb_args)
        if do_start:
            self.start_tween(tween, immediate=immediate)
        if self._logger:
            self._logger.debug("tween created for obj: %s attr: %s", obj.__class__, attr_name)
        return tween

    create_tween_by_change = create_tween

    def parallel(self, *tweens):
        """
        Creates a group of parallel running tweens.
        :param tweens: The tweens that should run in parallel.
        :return: parallel tween group
        """
        return _Parallel(self, *tweens)

    def next(self, *tweens):
        """
        Creates a group of tweens that will run on after one..
        :param tweens: The tweens that should run in series.
        :return: serial tween group
        """
        return _Serial(self, *tweens)

    def clear(self):
        """
        Removes all tweens from the tweener.
        """
        self._active_tweens[:] = []
        self._paused_tweens[:] = []
        if self._logger:
            self._logger.debug("cleared all tweens.")

    def pause_tweens(self):
        """
        Pauses all active tweens.
        """
        self._paused_tweens.extend(self._active_tweens)
        self._active_tweens[:] = []
        if self._logger:
            self._logger.debug("paused all tweens.")

    def resume_tweens(self):
        """
        Resumes all paused tweens.
        """
        self._active_tweens.extend(self._paused_tweens)
        self._paused_tweens[:] = []
        if self._logger:
            self._logger.debug("resume all tweens.")

    def pause_tween(self, tween):
        """
        Pauses the given tween.

        :param tween: The tween to pause (it just won't be updated, but is still registered).
        """
        for active in self._active_tweens:
            if tween == active:
                self._active_tweens.remove(active)
                self._paused_tweens.append(active)
                tween.state = self.TweenStates.paused
                if self._logger:
                    self._logger.debug("tween paused for obj: %s attr: %s", tween.o.__class__, tween.a)
                break
        else:
            if self._logger:
                self._logger.debug("tween not found for pausing for obj: %s attr: %s", tween.o.__class__, tween.a)

    def resume_tween(self, tween):
        """
        Resumes the given tween.

        :param tween: The tween to resume (it will be updated again).
        """
        for paused in self._paused_tweens:
            if tween == paused:
                self._paused_tweens.remove(paused)
                self._active_tweens.append(paused)
                tween.state = self.TweenStates.active
                if self._logger:
                    self._logger.debug("tween resumed for obj: %s attr: %s", tween.o.__class__, tween.a)
                break
            else:
                if self._logger:
                    self._logger.warning("trying to resume non existing or not paused tween for obj: %s attr: %s", tween
                                         .o.__class__, tween.a)
        else:
            if self._logger:
                self._logger.debug("tween not found for resuming for obj: %s attr: %s", tween.o.__class__, tween.a)

    def remove_tween(self, tween):
        """
        Removes the given tween from this tweener independent of its state (active as also paused tween are removed).

        :param tween: The tween to remove.
        """
        if tween in self._active_tweens:
            self._active_tweens.remove(tween)
        if tween in self._paused_tweens:
            self._paused_tweens.remove(tween)
        if self._logger:
            self._logger.debug("tween removed from active and paused for obj: %s attr: %s", tween.o.__class__, tween.a)
        tween.state = TweenStates.ended

    def get_all_tweens_for(self, obj, state=None):
        """
        Returns all tween for a given object according to the state filter. Raises an UnknownTweenStateException if a
        invalid state filter is provided.

        :param obj: The object where the tween operates on.
        :param state: The filter so only tween for that object in that state are returned. If set to None all tweens
            for that object are returned. See Tweener.TweenState.
        :return: List of tweens for the given object.
        """
        if state is not None and state not in TweenStateNames:
            raise UnknownTweenStateException(state)

        result = []
        if state is None or state == self.TweenStates.active:
            for tween in self._active_tweens:
                if tween.o == obj:
                    result.append(tween)
        if state is None or state == self.TweenStates.paused:
            for tween in self._paused_tweens:
                if tween.o == obj:
                    result.append(tween)
        if self._logger:
            self._logger.debug("get all tweens with filter '%s': %s", state, result)
        return result

    def start_tween(self, tween, immediate=True):
        """
        Starts a tween. If the tween is not created by the same instance of a tweener then a
        TweenBelongsToOtherTweenerException is raised.

        :param tween: The tween to start.
        :param immediate: If set to True, then the initial value is set directly after creation (even when delayed).
            Default is False.
        """
        tween.stop()

        if tween.tweener != self:
            raise TweenBelongsToOtherTweenerException("Tween has been created with another tweener!")

        # reset tween
        tween.t = -float(tween.delay)
        tween.v = tween.b

        # make it active
        self._active_tweens.append(tween)
        tween.state = self.TweenStates.active

        # calculate first value if immediate is True
        if immediate is True:
            value = tween.f(0.0, tween.b, tween.c, tween.d, tween.p)
            setattr(tween.o, tween.a, value)

    def get_all_tweens(self, state=None):
        """
        A method to retrieve the active and paused tweens.

        :param state: The filter for the state to query. All tweens are returned if set to None, otherwise take a
            look at Tweener.TweenState.
        :return: Returns a list of tweens, filtered by state if not None.
        """
        if state is not None and state not in TweenStateNames:
            raise UnknownTweenStateException(state)

        result = []
        if state is None or state == self.TweenStates.active:
            result += list(self._active_tweens)

        if state is None or state == self.TweenStates.paused:
            result += list(self._paused_tweens)

        return result


ease_functions = [

    ease_in_sine,
    ease_out_sine,
    ease_in_out_sine,
    ease_out_in_sine,

    ease_in_quad,
    ease_out_quad,
    ease_in_out_quad,
    ease_out_in_quad,

    ease_in_cubic,
    ease_out_cubic,
    ease_in_out_cubic,
    ease_out_in_cubic,

    ease_in_quart,
    ease_out_quart,
    ease_in_out_quart,
    ease_out_in_quart,

    ease_in_quint,
    ease_out_quint,
    ease_in_out_quint,
    ease_out_in_quint,

    ease_in_expo,
    ease_out_expo,
    ease_in_out_expo,
    ease_out_in_expo,

    ease_in_circ,
    ease_out_circ,
    ease_in_out_circ,
    ease_out_in_circ,

    ease_in_elastic,
    ease_out_elastic,
    ease_in_out_elastic,
    ease_out_in_elastic,

    ease_in_back,
    ease_out_back,
    ease_in_out_back,
    ease_out_in_back,

    ease_in_bounce,
    ease_out_bounce,
    ease_in_out_bounce,
    ease_out_in_bounce,

    ease_linear,
    ease_in_sine2,
    ease_in_sine3,
    ease_random_int_bounce,

]

logger.debug("imported")

if __name__ == '__main__':  # pragma: nocover

    def show_tweens_demo():  # pragma: nocover
        """
        The demo code for tweens. Shows some graphs.
        """

        class BoxWithLabel(object):

            # noinspection PyShadowingNames
            def __init__(self, box, label, label_dist=5):
                self.label = label
                self.rect = box
                # self.rect = box.inflate(2, 2)
                self.label_rect = label.get_rect(topleft=(box.left, box.bottom + label_dist))

            def draw(self, surf, color):
                pygame.draw.rect(surf, color, self.rect, 1)
                surf.blit(self.label, self.label_rect)

        class Slider(object):

            # noinspection PyShadowingNames
            def __init__(self, box, start, end, label):
                self.box = box
                self.start = start
                self.end = end
                self.label = label

            def draw(self, surf):
                start_pos = (self.start, self.box.centery)
                end_pos = (self.end, self.box.centery)
                pygame.draw.line(surf, grey, start_pos, end_pos, 3)
                pygame.draw.rect(surf, red, self.box)
                surf.set_at(self.box.center, white)
                surf.blit(self.label, (self.start, self.box.bottom + self.label.get_size()[1] / 3))

        # noinspection PyShadowingNames
        def reset(screen_w, tile_w, tile_h, spacing, margin, ease_functions, duration, trail_rects, boxes, tweener,
                  trails,
                  sliders):
            # clear
            trail_rects[:] = []
            boxes[:] = []
            trails.clear()
            tweener.clear()
            sliders[:] = []

            # calculate the coordinates for the boxes and sliders
            tile_w_spacing = tile_w + spacing
            tile_row_count = (screen_w - 2 * margin - tile_w - spacing) // tile_w_spacing
            slider_length = (screen_w - 2 * margin) // 4 - 10 * spacing
            slider_and_spacing = slider_length + 10 * spacing
            slider_row_count = (screen_w - 2 * margin) // slider_and_spacing
            label_h = 20
            for idx, func in enumerate(ease_functions):
                left = margin + idx % tile_row_count * tile_w_spacing
                top = margin + idx // tile_row_count * (tile_h + spacing + label_h)

                # tween objects
                r = pygame.Rect(0, 0, 3, 3)
                r.center = (left, top + tile_h)
                trail_rects.append(r)

                params = (-tile_h, 0) if func.__name__ == "ease_random_int_bounce" else None
                tweener.create_tween(r, "centerx", r.centerx, tile_w, duration, ease_linear)
                tweener.create_tween(r, "centery", r.centery, -tile_h, duration, func, params)
                trails[id(r)] = [r.center]  # add first point here so pygame.draw.lines has two points at first draw

                # boxes
                label = font.render(func.__name__, 1, white)
                box_rect = pygame.Rect(left, top, tile_w, tile_h)
                boxes.append(BoxWithLabel(box_rect, label))

                # sliders
                # left = margin + tile_row_count * tile_w_spacing
                left = margin + idx % slider_row_count * slider_and_spacing
                y = margin + idx // slider_row_count * 30 + screen_h // 2 + tile_h
                r = pygame.Rect(left, y, 7, 7)
                r.center = (left, y)

                params = (0, slider_length) if func.__name__ == "ease_random_int_bounce" else None
                tweener.create_tween(r, "centerx", r.centerx, slider_length, duration, func, params)
                slider = Slider(r, left, left + slider_length, label)
                sliders.append(slider)
                trails[id(slider)] = [slider.box.center]

        import pygame

        pygame.init()
        screen_w = 1024
        screen_h = 900

        pygame.display.set_caption("tweening, press any key to reset")
        screen = pygame.display.set_mode((screen_w, screen_h))
        font = pygame.font.Font(None, 15)

        red = (255, 0, 0)
        white = (255, 255, 255)
        grey = (90, 90, 90)
        blue1 = (155, 155, 255)
        blue = (0, 0, 255)

        tile_w = 100
        tile_h = 50
        spacing = 5
        margin = 10

        tween_objects = []
        boxes = []
        trails = {}  # {id : [points]]
        sliders = []
        duration = 2
        tweener = Tweener()
        reset(screen_w, tile_w, tile_h, spacing, margin, ease_functions, duration, tween_objects, boxes, tweener,
              trails,
              sliders)

        # instructions
        font30 = pygame.font.Font(None, 30)
        instructions_label = font30.render("Press any key to re-start. Escape or close the window to quit.", 1, white,
                                           grey)
        instr_rect = instructions_label.get_rect()
        instr_rect.centerx = screen_w * 0.5
        instr_rect.bottom = screen_h - margin

        clock = pygame.time.Clock()
        running = True

        # main loop
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    else:
                        reset(screen_w, tile_w, tile_h, spacing, margin, ease_functions, duration, tween_objects, boxes,
                              tweener, trails, sliders)

            # update
            dt = clock.tick(60) * 0.001  # convert to seconds
            tweener.update(dt)

            # record current position for drawing the trail
            for r in tween_objects:
                trails[id(r)].append(r.center)
            for s in sliders:
                trails[id(s)].append(s.box.center)

            # draw
            screen.fill((0, 0, 0))

            # draw boxes and sliders
            for idx, box in enumerate(boxes):
                box.draw(screen, blue1)
                sliders[idx].draw(screen)

            # draw trail of tweened objects
            for t in trails.values():
                # pygame.draw.lines(screen, grey, 0, t, 1)
                pygame.draw.lines(screen, blue, 0, t, 1)
                for p in t:
                    screen.set_at(p, white)

            # draw tweened objects
            for r in tween_objects:
                # pygame.draw.rect(screen, (255, 0, 0), r, 0)
                pygame.draw.circle(screen, red, r.center, 2)

            # draw instructions
            screen.blit(instructions_label, instr_rect)

            pygame.display.flip()


    def show_grouping_demo():  # pragma: no cover
        """
        Show the grouping of tweens.
        """
        import pygame

        pc = pygame.Color
        use_random_ease_function = False

        def activate_tween(the_tests, current):
            _test = the_tests[current]
            print()
            print("running", _test.__name__)
            _tween, _dots = _test(the_tweener, the_begin, the_change, the_duration)
            _tween.start()
            caption = "{0} |space: repeat |left/right arrow: prev/next test |f: {1} rand ease func |r: randomize".format(
                str(_test.__name__),
                str(use_random_ease_function))
            pygame.display.set_caption(caption)
            return _dots, [], _tween

        class Dot(object):

            def __init__(self, x=0, y=0, color=pygame.Color('white')):
                self.x = x
                self.y = y
                self.color = color
                self.radius = 5

        def rnd_ease():
            chose_ease_func = ease_linear
            if use_random_ease_function:
                import random
                chose_ease_func = random.choice(ease_functions)
            print('chosen ease_function:', chose_ease_func.__name__)
            return chose_ease_func

        def create_n_tweens(the_dots, tweener, begin, change, duration):
            count = len(the_dots)
            _t = []
            for i in range(count):
                _t.append(tweener.create_tween(the_dots[i], 'x', begin, change, duration, do_start=False,
                                               ease_function=rnd_ease()))
            return _t

        def create_n_dots(count, x, y, h, color=None):
            if color is None:
                color = [pygame.Color('white')]
            if len(color) < count:
                color = color * count
            _dots = []
            for i in range(count):
                _dots.append(Dot(x=x, y=y + i * h, color=color[i]))
            return _dots

        # noinspection PyUnusedLocal
        def one_after_other(tweener, begin, change, duration):
            _dots = create_n_dots(3, begin, 100, 50, color=[pc('red'), pc('green'), pc('blue')])
            _tween0, _tween1, _tween2 = create_n_tweens(_dots, tweener, begin, change, duration)
            _tween = _tween0.next(_tween1).next(_tween2)
            return _tween, _dots

        # noinspection PyUnusedLocal
        def repeat_tween_4_times(tweener, begin, change, duration):
            _dot = Dot(x=begin, y=100)
            _tween = tweener.create_tween(_dot, 'x', begin, change, duration, do_start=False, ease_function=rnd_ease())
            _tween = _tween.repeat(4)
            return _tween, [_dot]

        # noinspection PyUnusedLocal
        def repeat_serial_2_times(tweener, begin, change, duration):
            _dots = create_n_dots(2, begin, 100, 50)
            _t0, _t1 = create_n_tweens(_dots, tweener, begin, change, duration)
            s = _t0.next(_t1)  # create a serial
            _tween = s.repeat(2)
            return _tween, _dots

        # noinspection PyUnusedLocal
        def nested_serial(tweener, begin, change, duration):
            h = 50
            _dots = [
                Dot(x=begin, y=h + 1 * h, color=pygame.Color('red')),
                Dot(x=begin, y=h + 2 * h, color=pygame.Color('red')),
            ]

            _nest1, _dots1 = repeat_serial_2_times(tweener, begin, change, duration)
            for idx, _d in enumerate(_dots1):
                _d.color = pygame.Color('green')
                _d.y = 4 * h + idx * h

            _nest2, _dots2 = repeat_serial_2_times(tweener, begin, change, duration)
            for idx, _d in enumerate(_dots2):
                _d.color = pygame.Color('blue')
                _d.y = (len(_dots1) + 2) * h + (idx + len(_dots1)) * h

            _tween0 = tweener.create_tween(_dots[0], 'x', begin, change, duration, do_start=False,
                                           ease_function=rnd_ease())
            s = _tween0.next(
                tweener.create_tween(_dots[1], 'x', begin, change, duration, do_start=False, ease_function=rnd_ease()))
            _tween = s.next(_nest1.next(_nest2))
            return _tween, _dots + _dots1 + _dots2

        # noinspection PyUnusedLocal
        def parallel_2_tweens(tweener, begin, change, duration):
            _dots = create_n_dots(2, begin, 100, 50)
            _t1, _t2 = create_n_tweens(_dots, tweener, begin, change, duration)
            _p = _t1.parallel(_t2)
            return _p, _dots

        # noinspection PyUnusedLocal
        def two_series_of_parallels(tweener, begin, change, duration):
            _dots = create_n_dots(6, begin, 100, 50, color=[pc('red')] * 3 + [pc('green')] * 3)
            _t1, _t2, _t3, _t4, _t5, _t6 = create_n_tweens(_dots, tweener, begin, change, duration)
            p1 = _t1.parallel(_t2).parallel(_t3)
            p2 = _t4.parallel(_t5).parallel(_t6)
            s = p1.next(p2)
            return s, _dots

        # noinspection PyUnusedLocal
        def parallel_series(tweener, begin, change, duration):
            _dots = create_n_dots(6, begin, 100, 50, color=[pc('red')] * 3 + [pc('green')] * 3)
            _t1, _t2, _t3, _t4, _t5, _t6 = create_n_tweens(_dots, tweener, begin, change, duration)
            s1 = _t1.next(_t2).next(_t3)
            s2 = _t4.next(_t5).next(_t6)
            parallel = s1.parallel(s2)
            return parallel, _dots

        # noinspection PyUnusedLocal
        def nested_parallels(tweener, begin, change, duration):
            _dots = create_n_dots(3, begin, 100, 50, color=[pc('red'), pc('green'), pc('blue')])
            _t1, _t2, _t3 = create_n_tweens(_dots, tweener, begin, change, duration)
            parallel = _t1.parallel(_t2).parallel(_t3)
            return parallel, _dots

        # noinspection PyUnusedLocal
        def gumm_rgb_test_1(tweener, begin, change, duration):
            """move r, g, and b up and down in one series, repeated twice"""
            _dots = create_n_dots(4, begin, 100, 50, color=[pc('red'), pc('green'), pc('blue'), pc('grey')])

            TC = tweener.create_tween
            dum = TC(_dots[3], 'x', begin + 0, 1, 0.00001, do_start=False, ease_function=rnd_ease())
            rup = TC(_dots[0], 'x', begin + 0, 255, 1.0, do_start=False, ease_function=rnd_ease())
            gup = TC(_dots[1], 'x', begin + 0, 255, 1.0, do_start=False, ease_function=rnd_ease())
            bup = TC(_dots[2], 'x', begin + 255, -255, 1.0, do_start=False, ease_function=rnd_ease())
            r_down = TC(_dots[0], 'x', begin + 255, -255, 1.0, do_start=False, ease_function=rnd_ease())
            g_down = TC(_dots[1], 'x', begin + 0, 255, 1.0, do_start=False, ease_function=rnd_ease())
            b_down = TC(_dots[2], 'x', begin + 0, 1, 0.0001, do_start=False, ease_function=rnd_ease())
            chain = dum.next(
                rup.parallel(gup).parallel(bup)
            ).next(
                r_down.parallel(g_down).parallel(b_down)
            )

            # run_it('serial: RGB up/down twice', chain)
            return chain, _dots

        def example_c180_t1_next_t2(tweener, begin, change, duration):
            _dots = create_n_dots(2, begin, 100, 50)
            t1, t2 = create_n_tweens(_dots, tweener, begin, change, duration)
            chain = t1.next(t2)
            return chain, _dots

        def example_c182_t1_next_t2_t3_t4(tweener, begin, change, duration):
            _dots = create_n_dots(4, begin, 100, 50)
            t1, t2, t3, t4 = create_n_tweens(_dots, tweener, begin, change, duration)
            chain = t1.next(t2, t3, t4)
            return chain, _dots

        def example_c181_t1_parallel_t2(tweener, begin, change, duration):
            _dots = create_n_dots(2, begin, 100, 50)
            t1, t2 = create_n_tweens(_dots, tweener, begin, change, duration)
            chain = t1.parallel(t2)
            return chain, _dots

        def example_c183_t1_parallel_t2_t3_t4(tweener, begin, change, duration):
            _dots = create_n_dots(4, begin, 100, 50)
            t1, t2, t3, t4 = create_n_tweens(_dots, tweener, begin, change, duration)
            chain = t1.parallel(t2, t3, t4)
            return chain, _dots

        def example_c184_t1_repeat_3(tweener, begin, change, duration):
            _dots = create_n_dots(1, begin, 100, 50)
            t1 = create_n_tweens(_dots, tweener, begin, change, duration)[0]
            chain = t1.repeat(3)
            return chain, _dots

        # noinspection PyPep8Naming
        def example_c284_S_next_t2(tweener, begin, change, duration):
            _dots = create_n_dots(3, begin, 100, 50)
            t1, t2, t3 = create_n_tweens(_dots, tweener, begin, change, duration)
            series = t1.next(t2)
            chain = series.next(t3)
            return chain, _dots

        # noinspection PyPep8Naming
        def example_c285_S_next_t3_t4_t5(tweener, begin, change, duration):
            _dots = create_n_dots(5, begin, 100, 50)
            t1, t2, t3, t4, t5 = create_n_tweens(_dots, tweener, begin, change, duration)
            series = t1.next(t2)
            chain = series.next(t3, t4, t5)
            return chain, _dots

        # noinspection PyPep8Naming
        def example_c286_S_parallel_t3(tweener, begin, change, duration):
            _dots = create_n_dots(3, begin, 100, 50)
            t1, t2, t3 = create_n_tweens(_dots, tweener, begin, change, duration)
            t3.d *= 2  # make this tween last twice as long
            series = t1.next(t2)
            chain = series.parallel(t3)
            return chain, _dots

        # noinspection PyPep8Naming
        def example_c287_S_parallel_t3_t4_t5(tweener, begin, change, duration):
            _dots = create_n_dots(5, begin, 100, 50)
            t1, t2, t3, t4, t5 = create_n_tweens(_dots, tweener, begin, change, duration)
            t1.d /= 2  # make this tween twice as fast
            t2.d /= 2  # make this tween twice as fast
            series = t1.next(t2)
            chain = series.parallel(t3, t4, t5)
            return chain, _dots

        # noinspection PyPep8Naming
        def example_c288_S_repeat_3(tweener, begin, change, duration):
            _dots = create_n_dots(2, begin, 100, 50)
            t1, t2 = create_n_tweens(_dots, tweener, begin, change, duration)
            series = t1.next(t2)
            chain = series.repeat(3)
            return chain, _dots

        # noinspection PyPep8Naming
        def example_c388_P_next_t3(tweener, begin, change, duration):
            colors = [pc('dark green'), pc('dark green'), pc('white')]
            _dots = create_n_dots(3, begin, 100, 50, color=colors)
            t1, t2, t3 = create_n_tweens(_dots, tweener, begin, change, duration)
            parallel = t1.parallel(t2)
            chain = parallel.next(t3)
            return chain, _dots

        # noinspection PyPep8Naming
        def example_c389_P_next_t3_t4_t5(tweener, begin, change, duration):
            colors = [pc('dark green'), pc('dark green'), pc('white'), pc('white'), pc('white')]
            _dots = create_n_dots(5, begin, 100, 50, color=colors)
            t1, t2, t3, t4, t5 = create_n_tweens(_dots, tweener, begin, change, duration)
            parallel = t1.parallel(t2)
            chain = parallel.next(t3, t4, t5)
            return chain, _dots

        # noinspection PyPep8Naming
        def example_c390_P_parallel_t3(tweener, begin, change, duration):
            colors = [pc('dark green'), pc('dark green'), pc('white')]
            _dots = create_n_dots(3, begin, 100, 50, color=colors)
            t1, t2, t3 = create_n_tweens(_dots, tweener, begin, change, duration)
            parallel = t1.parallel(t2)
            chain = parallel.parallel(t3)
            return chain, _dots

        # noinspection PyPep8Naming
        def example_c391_P_parallel_t3_t4_t5(tweener, begin, change, duration):
            colors = [pc('dark green'), pc('dark green'), pc('white'), pc('white'), pc('white')]
            _dots = create_n_dots(5, begin, 100, 50, color=colors)
            t1, t2, t3, t4, t5 = create_n_tweens(_dots, tweener, begin, change, duration)
            parallel = t1.parallel(t2)
            chain = parallel.parallel(t3, t4, t5)
            return chain, _dots

        # noinspection PyPep8Naming
        def example_c392_P_repeat_3(tweener, begin, change, duration):
            _dots = create_n_dots(2, begin, 100, 50, color=[pc('dark green'), pc('dark green'), pc('white')])
            t1, t2 = create_n_tweens(_dots, tweener, begin, change, duration)
            parallel = t1.parallel(t2)
            chain = parallel.repeat(3)
            return chain, _dots

        def example_c493_t1_next__t2_parallel_t3(tweener, begin, change, duration):
            _dots = create_n_dots(3, begin, 100, 50)
            t1, t2, t3 = create_n_tweens(_dots, tweener, begin, change, duration)
            chain = t1.next(t2.parallel(t3))
            return chain, _dots

        def example_c494_t1_next__t2_parallel__t3_next_t4_repeat2(tweener, begin, change, duration):
            # T(1).next( T(2).parallel( T(3).next(T(4)).repeat(2) ) )
            _dots = create_n_dots(4, begin, 100, 50)
            t1, t2, t3, t4 = create_n_tweens(_dots, tweener, begin, change, duration)
            t2.d *= 4  # 4 times normal duration
            chain = t1.next(t2.parallel(t3.next(t4).repeat(2)))
            return chain, _dots

        def example_c495_t1_next_t2_t3_parallel_t4_t5(tweener, begin, change, duration):
            # c495 = T(1).next(T(2), T(3).parallel(T(4), T(5)))
            _dots = create_n_dots(5, begin, 100, 50)
            t1, t2, t3, t4, t5 = create_n_tweens(_dots, tweener, begin, change, duration)
            chain = t1.next(t2, t3.parallel(t4, t5))
            return chain, _dots

        def example_c496_t1_parallel_t2_parallel_t3_t4_t5_parallel_t6(tweener, begin, change, duration):
            # c496 = T(1).parallel(T(2)).parallel(T(3), T(4), T(5)).parallel(T(6))  # -> S(P(1, 2), P(3, 4, 5, 6))
            _dots = create_n_dots(6, begin, 100, 50)
            t1, t2, t3, t4, t5, t6 = create_n_tweens(_dots, tweener, begin, change, duration)
            chain = t1.parallel(t2.parallel(t3, t4, t5.parallel(t6)))
            return chain, _dots

        # noinspection PyPep8Naming
        def example_G_c496_t1_parallel_t2_parallel_t3_t4_t5_parallel_t6(tweener, begin, change, duration):
            # c496 = T(1).parallel(T(2)).parallel(T(3), T(4), T(5)).parallel(T(6))  # -> S(P(1, 2), P(3, 4, 5, 6))
            _dots = create_n_dots(6, begin, 100, 50)
            t1, t2, t3, t4, t5, t6 = create_n_tweens(_dots, tweener, begin, change, duration)
            # chain = t1.parallel(t2.parallel(t3, t4, t5.parallel(t6)))
            tweener = t1.tweener
            chain = _Parallel(tweener, t1, _Parallel(tweener, t2, t3, t4, _Parallel(tweener, t5, t6)))
            return chain, _dots

        def example_c497_t1_parallel_t2__t3_next_t4_next_t5__t6(tweener, begin, change, duration):
            # c497 = T(1).parallel(T(2), T(3)).next(T(4)).next(T(5), T(6))  # -> S(P(1, 2, 3), T4, P(5, 6))
            _dots = create_n_dots(6, begin, 100, 50)
            t1, t2, t3, t4, t5, t6 = create_n_tweens(_dots, tweener, begin, change, duration)
            t1.d *= 3
            t2.d *= 3
            t6.d *= 3
            chain = t1.parallel(t2, t3.next(t4).next(t5), t6)
            return chain, _dots

        # noinspection PyPep8Naming
        def example_G_c497_t1_parallel_t2__t3_next_t4_next_t5__t6(tweener, begin, change, duration):
            # c497 = T(1).parallel(T(2), T(3)).next(T(4)).next(T(5), T(6))  # -> S(P(1, 2, 3), T4, P(5, 6))
            _dots = create_n_dots(6, begin, 100, 50)
            t1, t2, t3, t4, t5, t6 = create_n_tweens(_dots, tweener, begin, change, duration)
            t1.d *= 3
            t2.d *= 3
            t6.d *= 3
            # chain = t1.parallel(t2, t3.next(t4).next(t5), t6)
            tweener = t1.tweener
            chain = _Parallel(tweener, t1, t2, _Serial(tweener, t3, t4, t5), t6)
            return chain, _dots

        pygame.init()
        the_screen_size = (800, 600)
        screen = pygame.display.set_mode(the_screen_size)
        clock = pygame.time.Clock()
        the_tweener = Tweener()

        the_begin = 100
        the_change = 200
        the_duration = 1
        tests = [
            # repeat_tween_4_times,
            # one_after_other,
            # repeat_serial_2_times,
            # nested_serial,
            # parallel_2_tweens,
            # two_series_of_parallels,
            # parallel_series,
            # nested_parallels,
            # gumm_rgb_test_1,

            example_c180_t1_next_t2,
            example_c181_t1_parallel_t2,
            example_c182_t1_next_t2_t3_t4,
            example_c183_t1_parallel_t2_t3_t4,
            example_c184_t1_repeat_3,

            example_c284_S_next_t2,
            example_c285_S_next_t3_t4_t5,
            example_c286_S_parallel_t3,
            example_c287_S_parallel_t3_t4_t5,
            example_c288_S_repeat_3,

            example_c388_P_next_t3,
            example_c389_P_next_t3_t4_t5,
            example_c390_P_parallel_t3,
            example_c391_P_parallel_t3_t4_t5,
            example_c392_P_repeat_3,

            example_c493_t1_next__t2_parallel_t3,
            example_c494_t1_next__t2_parallel__t3_next_t4_repeat2,
            example_c495_t1_next_t2_t3_parallel_t4_t5,
            example_c496_t1_parallel_t2_parallel_t3_t4_t5_parallel_t6,
            example_G_c496_t1_parallel_t2_parallel_t3_t4_t5_parallel_t6,
            example_c497_t1_parallel_t2__t3_next_t4_next_t5__t6,
            example_G_c497_t1_parallel_t2__t3_next_t4_next_t5__t6,
        ]
        current_test = -1
        dots, trails, current_tween = activate_tween(tests, current_test)

        running = True
        while running:
            # eventing
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_r:
                        dots, trails, current_tween = activate_tween(tests, current_test)
                    elif event.key == pygame.K_SPACE:
                        for d in dots:
                            d.x = the_begin
                        current_tween.start(immediate=True)
                    elif event.key in (pygame.K_RIGHT, pygame.K_LEFT):
                        current_test += -1 if event.key == pygame.K_LEFT else 1
                        current_test %= len(tests)
                        dots, trails, current_tween = activate_tween(tests, current_test)
                    elif event.key == pygame.K_f:
                        use_random_ease_function = not use_random_ease_function

            # update
            dt = clock.tick(30) / 1000.0  # convert to seconds
            the_tweener.update(dt)

            # draw
            screen.fill((0, 0, 0))
            screen.fill((50, 50, 50), pygame.Rect(the_begin, 0, the_change, the_screen_size[1]))
            for trail in trails:
                pygame.draw.circle(*trail)

            for dot in dots:
                pygame.draw.circle(screen, dot.color, (int(dot.x), int(dot.y)), dot.radius)
                trails.append((screen, dot.color, (int(dot.x), int(dot.y)), 2))

            pygame.display.flip()


    def show_vector_demo():
        """
        Apply tweening to a Vector2 attribute.
        """
        import pygame

        pygame.init()
        screen_w = 1024
        screen_h = 900

        pygame.display.set_caption("tweening vectors, press any key to reset")
        screen = pygame.display.set_mode((screen_w, screen_h))
        font = pygame.font.Font(None, 15)

        red = (255, 0, 0)
        white = (255, 255, 255)
        grey = (90, 90, 90)
        yellow = (155, 155, 0)
        blue = (0, 0, 255)

        class FlyingSaucer(object):

            def __init__(self):
                self.position = pygame.Vector2(100, 100)
                self.prev_position = pygame.Vector2()
                self.update()

            def update(self):
                self.prev_position.update(self.position)

            def draw_arrow(self, screen, scale=1.0):
                direction = (self.position - self.prev_position) * scale
                end = self.position + direction
                to_mid = direction * 0.33
                if to_mid.length() > 10:
                    to_mid = to_mid.normalize() * 10
                mid = end - to_mid
                left = mid + (end - mid).rotate(90)
                right = mid + (end - mid).rotate(-90)
                pygame.draw.line(screen, yellow, self.position, end, 3)
                pygame.draw.line(screen, yellow, end, left, 3)
                pygame.draw.line(screen, yellow, end, right, 3)


        duration = 10
        tweener = Tweener()

        vector_ease_functions = [

            ease_in_sine,
            ease_out_sine,
            ease_in_out_sine,
            ease_out_in_sine,

            ease_in_quad,
            ease_out_quad,
            ease_in_out_quad,
            ease_out_in_quad,

            ease_in_cubic,
            ease_out_cubic,
            ease_in_out_cubic,
            ease_out_in_cubic,

            ease_in_quart,
            ease_out_quart,
            ease_in_out_quart,
            ease_out_in_quart,

            ease_in_quint,
            ease_out_quint,
            ease_in_out_quint,
            ease_out_in_quint,

            ease_in_expo,
            ease_out_expo,
            ease_in_out_expo,
            ease_out_in_expo,

            ease_in_circ,
            ease_out_circ,
            ease_in_out_circ,
            ease_out_in_circ,

            # ease_in_elastic,
            # ease_out_elastic,
            # ease_in_out_elastic,
            # ease_out_in_elastic,
            #
            ease_in_back,
            ease_out_back,
            ease_in_out_back,
            ease_out_in_back,
            #
            # ease_in_bounce,
            # ease_out_bounce,
            # ease_in_out_bounce,
            # ease_out_in_bounce,

            ease_linear,
            ease_in_sine2,
            ease_in_sine3,
            # ease_random_int_bounce,

        ]
        dist = 10
        saucers = []
        for idx, ease in enumerate(vector_ease_functions):
            y = idx * dist + dist
            flying_saucer = FlyingSaucer()
            flying_saucer.position.y = y
            flying_saucer.update()
            start = flying_saucer.position.copy()
            target = start + pygame.Vector2(300, y)

            tween = tweener.create_tween_by_end(flying_saucer, "position", start,
                                                target, duration, ease)
            saucers.append(flying_saucer)

        clock = pygame.time.Clock()
        running = True

        pygame.event.clear()

        # main loop
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    else:
                        # reset
                        flying_saucer.position.update(start)
                        tweener.clear()
                        tween = tweener.create_tween_by_end(flying_saucer, "position", start,
                                                            target, duration,
                                                            ease_out_bounce)

            # update
            for flying_saucer in saucers:
                flying_saucer.update()  # store current position
            dt = clock.tick(60) * 0.001  # convert to seconds
            tweener.update(dt)

            # draw
            screen.fill((0, 0, 0))

            # draw tweened objects
            for flying_saucer in saucers:
                pygame.draw.circle(screen, red, start, 5)
                pygame.draw.circle(screen, blue, target, 5)
                pygame.draw.line(screen, grey, start, target)
                pygame.draw.circle(screen, white, flying_saucer.position, 20)

                flying_saucer.draw_arrow(screen, 25)

            pygame.display.flip()


    show_vector_demo()
    show_tweens_demo()
    show_grouping_demo()
