# Initial processing times tau_{t,m}
tau = {
    (1, 1): 3, (1, 2): 3, (1, 3): 2,
    (2, 1): 4, (2, 2): 2, (2, 3): 2,
    (3, 1): 2, (3, 2): 1, (3, 3): 4,
}

# Machine speeds speed_m
speed = {1: 2, 2: 2, 3: 2}

# Adjusted processing times
adjusted_tau = {(t, m): tau[(t, m)] / speed[m] for (t, m) in tau}

# Print the adjusted processing times
print("Adjusted Processing Times:")
for key, value in adjusted_tau.items():
    print(f"tau{key} = {value}")
