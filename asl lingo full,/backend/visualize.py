import sys
import json

import matplotlib.pyplot as plt
import numpy as np

fig = plt.figure()
ax = fig.add_subplot(projection='3d')

with open("stored.json") as file:
    stored = json.load(file)
filename = sys.argv[1]
for name, stored_positions in stored.items():
    for positions, stored_filename in stored_positions:
        if stored_filename == filename:
            break
    else: continue
    break
else:
    exit("not found")

P1 = positions

ax.scatter(*zip(*P1[:]), marker="o")

ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')

plt.show()
