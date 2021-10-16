#! python3

from solaredge import SolarEdgeConnector
from plot import SolarPlot

# Get data
sec = SolarEdgeConnector()
sec.get_sites_list()
component_power, component_status, connections, battery_level = sec.get_site_power_flow(0)

# Plot
plot = SolarPlot()
plot.power_flow(component_power, component_status, connections)
plot.show_all()
