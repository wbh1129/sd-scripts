#!/usr/bin/env python3
# Precomputed learning schedules can be found in the clr directory

from math import *
import argparse

parser = argparse.ArgumentParser(
        description="cyclical learning rates for Auto1111 training",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
)
parser.add_argument("--max", default=2e-4, type=float, help="cycle peak value")
parser.add_argument("--min", default=6, type=float, help="cycle minimum value (as a fraction of --max), recommended 5-10")
parser.add_argument("--len", default=10, type=int, help="cycle length, recommended (2-10) * steps_per_epoch")
parser.add_argument("--cycles", default=50, type=int, help="quantity of cycles to generate")
parser.add_argument("--decay", default=0.0, type=float, help="rate of decay")
parser.add_argument("--no-restarts", action="store_true", help="do full waves instead of half")
parser.add_argument("--start", default=2, type=int, help="wave start point; 0 for min; 1 for max; 2 for full wave followed by max")
parser.add_argument("--start-len", default=1, type=int, help="length of first wave if --start=2 (as a multiple of --len)")
parser.add_argument("--onecycle", default=0, type=int, help="1cycle phase length, 0 to disable")
parser.add_argument("--onecycle-min", default=10, type=float, help="1cycle phase minimum (as a fraction of --min), recommended 10-100 ")
parser.add_argument("--step-start", default=0, type=int, help="starting point for steps, useful for resuming training w/ a new schedule")
parser.add_argument("--wave", default=1, type=int, help="0 for triangle; 1 for sine")
parser.add_argument("--plot", action="store_true", help="show a plot of the LR schedule w/ matplotlib")
ARGS = parser.parse_args()

ARGS.min = ARGS.max / ARGS.min
ARGS.onecycle_min = ARGS.min / ARGS.onecycle_min

# TODO add variable length cycles
# TODO maybe refactor so the rates array is an array of arrays

if ARGS.onecycle > 0:
    ARGS.cycles=1
    ARGS.start=0
    ARGS.no_restarts = True

def transform_wave(func):
    def wrap(*args, **kwargs):
        val = func(*args, **kwargs)
        if ARGS.wave == 1:
            return sin(val * pi/2)
        else:
            return val
    return wrap

@transform_wave
def saw(start, i, c_len):
    return abs(start - (i%c_len) / (c_len-1))

# FIXME screwy
@transform_wave
def tri(start, i, c_len):
    return abs(1-start - abs(i%(2*c_len-1) - (c_len-1)) / (c_len-1))

rates = []

if ARGS.start == 2:
    firstwave = lambda i: tri(0, i, ceil(ARGS.len/2)*ARGS.start_len)
    rates = [ARGS.min * (1 - firstwave(i)) + ARGS.max * firstwave(i) for i in range(ARGS.len * ARGS.start_len - 1)] + rates;
    ARGS.start=1

if ARGS.no_restarts:
    FULL_CYCLE_LEN=2*(ARGS.len-1)
    STEPS=FULL_CYCLE_LEN*ARGS.cycles+1
    wave = lambda i: tri(ARGS.start, i, ARGS.len)
else:
    FULL_CYCLE_LEN=ARGS.len
    STEPS=ARGS.len*ARGS.cycles
    wave = lambda i: saw(ARGS.start, i, ARGS.len)

decay = lambda v,i: v / (1 + i//FULL_CYCLE_LEN * ARGS.decay)

rates += [decay(ARGS.min,i) * (1 - wave(i)) + decay(ARGS.max,i) * wave(i)
          for i in range(FULL_CYCLE_LEN * int(bool(len(rates))), STEPS - len(rates) - 1)]

if ARGS.onecycle > 0:
    wave_1cyc = lambda i: tri(0, i, ARGS.onecycle+1)
    rates += [ARGS.min * (1 - wave_1cyc(i)) + ARGS.onecycle_min * wave_1cyc(i) for i in range(1, ARGS.onecycle+1)]

rates_str = [f"{x:.2e}:{i+1+ARGS.step_start}" for (i,x) in enumerate(rates)]
rates_str[-1] = rates_str[-1].split(":")[0] # coast on final LR
print(", ".join(rates_str))

if ARGS.plot:
    import matplotlib.pyplot as plt
    plt.plot(range(1, len(rates)+1), rates)
    plt.grid()
    plt.title(f"Avg: {sum(rates)/len(rates)}")
    plt.show()
