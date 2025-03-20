import nl4py
import sys
import time

# Specify the location of your NetLogo installation
netlogo_home = "C:/Program Files/NetLogo 6.2.2"  # adjust this path as needed

# Initialize the NL4Py server with your NetLogo installation path
nl4py.initialize(netlogo_home)

# Start the NetLogo application (GUI mode)
netlogo_app = nl4py.netlogo_app()

# Define the path to the NetLogo model (e.g., Fire.nlogo)
model_path = "path/to/Fire.nlogo"  # replace with the actual path to your model
netlogo_app.open_model(model_path)

# Optionally set the model parameters to random values
netlogo_app.set_params_random()

# Run the model commands: first setup, then execute 100 steps
netlogo_app.command("setup")
netlogo_app.command("repeat 100 [ go ]")

# Pause briefly to ensure simulation progress (if necessary)
time.sleep(5)

# Retrieve a reporter value from the model (e.g., number of burned trees)
burned_trees = netlogo_app.report("burned-trees")
print("Number of burned trees:", burned_trees)

# Close the model when finished
netlogo_app.close_model()
