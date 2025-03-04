import matplotlib.pyplot as plt
import numpy as np

# Time values
t = np.linspace(0, 2000, 1000)

# Worker speed values for different conditions (M0, f=0, with different decay factors)
speed_0 = np.ones_like(t)
speed_001 = 1-np.exp(-0.001 * (t % 500))  # Decay factor 0.001, reset every 500 units of time
speed_002 = 1- np.exp(-0.002 * (t % 500))  # Decay factor 0.002, reset every 500 units of time

# Plotting the curves
plt.plot(t, speed_0, label="$\lambda_F$=0")
plt.plot(t, speed_001, label="$\lambda_F$=0.001")
plt.plot(t, speed_002, label="$\lambda_F$=0.002")

# Setting the x and y axis limits
plt.xlim(0, 2000)  # Set xmin and xmax
plt.ylim(-0.5, 2.5)  # Set ymin and ymax

# Labeling the axes
plt.xlabel("t", fontsize=14)  # Increased font size for x-axis label
plt.ylabel("worker's speed (t)", fontsize=14)  # Increased font size for y-axis label

# Adding the legend with larger font size
plt.legend(fontsize=12)

# Save the figure as a PDF
plt.savefig("worker_speed_plot.pdf")

# Displaying the plot
plt.show()
