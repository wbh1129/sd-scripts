#!/usr/bin/env python3
# plots textual_inversion_loss.csv with matplotlib

import pandas as pd
import matplotlib.pyplot as plt
import sys

if len(sys.argv) > 1:
    file = sys.argv[1]
else:
    file = "textual_inversion_loss.csv"

csv = pd.read_csv(file)
loss, learn = csv.plot("step", ["loss","learn_rate"], style=[":",""],
                       subplots=True, sharex=False, grid=True)

avg = lambda arr: sum(arr)/len(arr)
avg_loss = lambda r: [avg(csv["loss"][max(i-r,0):i+r+1]) for i in range(len(csv["loss"]))]
avg_loss_unidirectional = lambda r: [avg(csv["loss"][max(i-r,0):i+1]) for i in range(len(csv["loss"]))]
recent_min = lambda r: [min(csv["loss"][max(i-r,0):i+1]) for i in range(len(csv["loss"]))]

loss.plot(csv["step"], avg_loss_unidirectional(3), "b", linewidth=2, label="avg")
loss.plot(csv["step"], recent_min(3), "r", linewidth=2, label="min")
loss.set_title(f"Min: {min(csv['loss'])}, Max: {max(csv['loss'])}, Avg: {avg(csv['loss'])}")
loss.legend()

learn.set_title(f"Min: {min(csv['learn_rate'])}, Max: {max(csv['learn_rate'])}, Avg: {avg(csv['learn_rate'])}")
plt.show()

