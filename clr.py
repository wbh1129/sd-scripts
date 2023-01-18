#!/usr/bin/env python3

from math import *

# The recommended values are just based on things I read online. Please feel 
# free to experiment, let me know if you find anything interesting!

MAX=2e-4
MIN=MAX/6 # recommended value is MAX/6
CYCLE_LEN=10 # cycle length, recommended (2-10) * steps_per_epoch
CYCLES=50 # number of cycles to generate
DECAY=0.0 # lower numbers decay slower, higher numbers decay faster, 0 disables decay
RESTARTS=1 # 1 for half wave, 0 for full wave (CYCLE_LEN is doubled)
START=2 # 2 for single full wave prior to half waves, 1 to start at MAX, 0 to start at MIN
ONECYCLE=0 # 1cycle phase length, 0 to disable
ONECYCLE_MIN=MIN/100
STEP_OFF=0 # step offset, for resuming training with a different schedule
WAVE=1 # 1 for sine, 0 for triangle/sawtooth
PLOT=0 # plot out the learning rate schedule w/ matplotlib

# TODO add variable length cycles

if ONECYCLE > 0:
    CYCLES=1
    START=0
    RESTARTS=0

def transform_wave(func):
    def wrap(*args, **kwargs):
        val = func(*args, **kwargs)
        if WAVE == 1:
            return sin(val * pi/2)
        else:
            return val
    return wrap

@transform_wave
def saw(start, i, c_len):
    return abs(start - (i%c_len) / (c_len-1))

@transform_wave
def tri(start, i, c_len):
    return abs(1-start - abs(i%(2*c_len-1) - (c_len-1)) / (c_len-1))

rates = []

if START == 2:
    firstwave = lambda i: tri(0, i, ceil(CYCLE_LEN/2))
    rates = [MIN * (1 - firstwave(i)) + MAX * firstwave(i) for i in range(CYCLE_LEN-1)] + rates;
    START=1

if RESTARTS == 1:
    FULL_CYCLE_LEN=CYCLE_LEN
    STEPS=CYCLE_LEN*CYCLES
    wave = lambda i: saw(START, i, CYCLE_LEN)
else:
    FULL_CYCLE_LEN=2*(CYCLE_LEN-1)
    STEPS=FULL_CYCLE_LEN*CYCLES+1
    wave = lambda i: tri(START, i, CYCLE_LEN)

decay = lambda v,i: v / (1 + i//FULL_CYCLE_LEN * DECAY)

rates += [decay(MIN,i) * (1 - wave(i)) + decay(MAX,i) * wave(i) for i in range(STEPS)]

if ONECYCLE > 0:
    wave_1cyc = lambda i: tri(0, i, ONECYCLE+1)
    rates += [MIN * (1 - wave_1cyc(i)) + ONECYCLE_MIN * wave_1cyc(i) for i in range(1, ONECYCLE+1)]

rates_str = [f"{x:.2e}:{i+1+STEP_OFF}" for (i,x) in enumerate(rates)]
rates_str[-1] = rates_str[-1].split(":")[0] # coast on final LR
print(", ".join(rates_str))

if PLOT == 1:
    import matplotlib.pyplot as plt
    plt.plot(range(1, len(rates)+1), rates)
    plt.grid()
    plt.title(f"Avg: {sum(rates)/len(rates)}")
    plt.show()
