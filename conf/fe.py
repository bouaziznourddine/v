import matplotlib.pyplot as plt
import numpy as np

# Time values
t = np.linspace(0, 2000, 1000)

# Worker speed decay with reset and spike at regular intervals
f = 0.002  # Decay factor
e = 0.2    # Spike after reset
speed = np.exp(-f * (t % 500)) + (t // 500) * e  # Speed decay with reset every 500 units, and increase by 'e'

# Plotting the curve
plt.plot(t, speed, label="$\lambda_F$=0.002,$\lambda_E$=0.2")

# Setting the x and y axis limits
plt.xlim(0, 2000)  # Set xmin and xmax
plt.ylim(-0.5, 2.5)  # Set ymin and ymax

# Labeling the axes
plt.xlabel("t", fontsize=14)
plt.ylabel("worker's speed (t)", fontsize=14)

# Adding the legend
plt.legend(fontsize=12)

# Display the plot
plt.show()
