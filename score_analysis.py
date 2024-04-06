import json
from matplotlib import pyplot as plt
import numpy as np

with open('./LunarLander/high_scores.json', 'r') as json_file:
    scores = json.load(json_file)

flight_time = []
fuel_level = []
overall_score = []

for score in scores:
    flight_time.append(score['flight_time'])
    fuel_level.append(score['fuel_remaining'])
    overall_score.append(score['score'])

# Scatter plot with color encoding
plt.figure(figsize=(10, 6))
plt.scatter(flight_time, overall_score, s=fuel_level,
            c=fuel_level, cmap='coolwarm', alpha=0.7)
plt.colorbar(label='Fuel Level')
plt.xlabel('Flight Time')
plt.ylabel('Overall Score')
plt.title('Flight Time vs Overall Score with Fuel Level')
plt.grid(True)
plt.show()

# Bubble chart
plt.figure(figsize=(10, 6))
plt.scatter(flight_time, overall_score, s=fuel_level*5, alpha=0.5)
plt.xlabel('Flight Time')
plt.ylabel('Overall Score')
plt.title('Bubble Chart: Flight Time vs Overall Score with Fuel Level')
plt.grid(True)
plt.show()

# 3D Scatter Plot

fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')
ax.scatter(flight_time, overall_score, fuel_level,
           c=fuel_level, cmap='coolwarm')
ax.set_xlabel('Flight Time')
ax.set_ylabel('Overall Score')
ax.set_zlabel('Fuel Level')
ax.set_title('3D Scatter Plot: Flight Time vs Overall Score vs Fuel Level')
plt.show()

# Line Plot with Dual Y-axis (assuming time as x-axis)
time = np.arange(1, 51)

fig, ax1 = plt.subplots(figsize=(10, 6))

ax1.plot(time, flight_time, 'b-', label='Flight Time')
ax1.set_xlabel('Time')
ax1.set_ylabel('Flight Time', color='b')
ax1.tick_params('y', colors='b')

ax2 = ax1.twinx()
ax2.plot(time, fuel_level, 'r-', label='Fuel Level')
ax2.plot(time, overall_score, 'g-', label='Overall Score')
ax2.set_ylabel('Fuel Level & Overall Score', color='r')
ax2.tick_params('y', colors='r')

fig.tight_layout()
plt.title(
    'Line Plot with Dual Y-axis: Flight Time, Fuel Level, and Overall Score over Time')
plt.show()
