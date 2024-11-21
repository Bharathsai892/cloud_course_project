#!/usr/bin/python3

import matplotlib
matplotlib.use('TkAgg')  # Ensure TkAgg backend for GUI

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from mn_wifi.net import Mininet_wifi
from mininet.node import Controller
from mn_wifi.node import OVSKernelAP
from mininet.link import TCLink
from mininet.log import setLogLevel, info
from mn_wifi.cli import CLI
import traci  # Import TraCI library
import os
import time

# Set up SUMO command and configuration
SUMO_BINARY = "sumo-gui"  # Use "sumo" for command-line, or "sumo-gui" for graphical
SUMO_CONFIG = "main.sumocfg"  # Path to SUMO config file

# Define the topology
def topology():
    "Create a network."
    net = Mininet_wifi(
        controller=Controller,
        link=TCLink,
        accessPoint=OVSKernelAP,
        plot=True  # Enable built-in plotting
    )

    info("*** Creating nodes\n")
    
    # Add controller
    c1 = net.addController('c1')

    # Add and configure access points with corrected range
    ap1 = net.addAccessPoint('ap1', 
                            ssid='RSU1',
                            mode='g',
                            channel='1',
                            position='50,50,0',
                            failMode='standalone',
                            range=120)
    
    ap2 = net.addAccessPoint('ap2',
                            ssid='RSU2',
                            mode='g',
                            channel='6',
                            position='150,50,0',
                            failMode='standalone',
                            range=120)

    # Add cars (stations) with corrected range
    cars = []
    for i in range(5):
        car = net.addStation(
            name='car%d' % (i + 1),
            mac='00:00:00:00:00:%02d' % (i + 1),
            ip='10.0.0.%d/24' % (i + 1),
            position='%d,30,0' % (50 + i * 20),
            range=120
        )
        cars.append(car)

    info("*** Configuring wifi nodes\n")
    net.configureWifiNodes()

    info("*** Creating links\n")
    net.addLink(ap1, c1)
    net.addLink(ap2, c1)

    info("*** Starting network\n")
    net.build()
    c1.start()
    ap1.start([c1])
    ap2.start([c1])

    # Start SUMO with TraCI
    traci.start([SUMO_BINARY, "-c", SUMO_CONFIG])
    time.sleep(1)  # Give SUMO some time to start

    # Create the figure and axis for the plot
    fig, ax = plt.subplots()
    ax.set_xlim(0, 300)
    ax.set_ylim(0, 150)

    # Create scatter plots for access points and cars (stations)
    ap1_plot, = ax.plot([], [], 'ro', label="AP1")
    ap2_plot, = ax.plot([], [], 'bo', label="AP2")
    cars_plots = [ax.plot([], [], 'go')[0] for _ in range(5)]

    # Function to update car positions in Mininet-WiFi based on SUMO positions
    def update_car_positions():
        for car in cars:
            car_id = car.name
            if traci.vehicle.isVehicleStopped(car_id):
                continue
            
            # Get vehicle position from SUMO
            x, y = traci.vehicle.getPosition(car_id)
            # Update Mininet-WiFi car position
            car.setPosition(f"{x},{y},0")
            info(f"Updated position for {car.name}: {x}, {y}\n")

    # Function to update the plot with the new car positions
    def update_plot(frame):
    # Update the access point positions (static)
        ap1_plot.set_data(50, 50)
        ap2_plot.set_data(150, 50)

        # Update each car's position
        for i, car in enumerate(cars):
            # Ensure that 'position' exists in params
            if 'position' in car.params:
                x, y, z = car.params['position']  # Access position from car.params
                cars_plots[i].set_data(x, y)  # Update the car position on the plot
            else:
                # Handle missing position (e.g., set to origin or skip)
                cars_plots[i].set_data(0, 0)  # Set to (0, 0) or any default value

        return [ap1_plot, ap2_plot] + cars_plots



    # Set up the animation
    ani = FuncAnimation(fig, update_plot, frames=range(100), interval=500, blit=True)

    # Show the plot in the main thread
    plt.legend()
    plt.show()  # Use plt.show() directly in the main thread

    try:
        # Main loop for updating car positions from SUMO
        while True:
            traci.simulationStep()  # Advance SUMO simulation
            update_car_positions()  # Update Mininet-WiFi car positions
            net.updateNodePos()  # Refresh network positions in Mininet-WiFi
            time.sleep(0.1)  # Adjust for appropriate time step
    except KeyboardInterrupt:
        pass
    finally:
        # Close SUMO
        traci.close()

    info("*** Running CLI\n")
    CLI(net)

    info("*** Stopping network\n")
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    topology()
