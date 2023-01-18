#!/usr/bin/env python3

import pandas as pd
import matplotlib.pyplot as plt

csv = pd.read_csv("textual_inversion_loss.csv")
loss, learn = csv.plot("step", ["loss","learn_rate"], style=[":",""],
                       subplots=True, sharex=False, grid=True)

avg      = lambda arr: sum(arr)/len(arr)
avg_loss = lambda r: [avg(csv["loss"][max(i-r,0):i+r+1])
                      for i in range(len(csv["loss"]))]

loss.plot(csv["step"], avg_loss(5), "r", linewidth=2, label="avg5")
loss.plot(csv["step"], avg_loss(10), "b", linewidth=2, label="avg10")
loss.set_title(f"Min: {min(csv['loss'])}, Max: {max(csv['loss'])}, Avg: {avg(csv['loss'])}")
loss.legend()

learn.set_title(f"Min: {min(csv['learn_rate'])}, Max: {max(csv['learn_rate'])}, Avg: {avg(csv['learn_rate'])}")
plt.show()

