import matplotlib.pyplot as plt
import numpy as np

# Time values
t = np.arange(0, 2100, 500)

# Worker speed values for different conditions (M0, f=0, e=0; M0, f=0, e=0.1; M0, f=0, e=0.2)
speed_0 = [1, 1, 1, 1, 1]
speed_01 = [1, 1, 1.1, 1.2, 1.3]
speed_02 = [1, 1.2, 1.3, 1.5, 1.7]

# Plotting step plots
plt.step(t, speed_0, label="$\lambda_E$=0", where="post")
plt.step(t, speed_01, label="$\lambda_E$=0.1", where="post")
plt.step(t, speed_02, label="$\lambda_E$=0.2", where="post")

# Labeling the axes
plt.xlabel("t")
plt.ylabel("worker's speed (t)")
plt.xlim(0, 2000)  # Set xmin and xmax
plt.ylim(0, 2.5)  # Set ymin and ymax
# Adding the legend
plt.legend(fontsize=12)
# Labeling the axes with larger font sizes
plt.xlabel("t", fontsize=14)  # Increased font size for x-axis label
plt.ylabel("worker's speed (t)", fontsize=14)  # Increased font size for y-axis label



# Displaying the plot
plt.show()