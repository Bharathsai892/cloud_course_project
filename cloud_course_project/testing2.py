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

    # Helper function to move cars
    def move_car(car, new_x, new_y):
        car.setPosition('%d,%d,0' % (new_x, new_y))
        net.mobility.set_mp(car)  # Update the plot

    # Add the move_car function to the network object for CLI access
    net.move_car = move_car

    # Create the figure and axis for the plot
    fig, ax = plt.subplots()
    ax.set_xlim(0, 300)
    ax.set_ylim(0, 150)

    # Create scatter plots for access points and cars (stations)
    ap1_plot, = ax.plot([], [], 'ro', label="AP1")
    ap2_plot, = ax.plot([], [], 'bo', label="AP2")
    cars_plots = [ax.plot([], [], 'go')[0] for _ in range(5)]

    # Function to update the plot with the new car positions
    def update_plot(frame):
        # Update the access point positions (static)
        ap1_plot.set_data(50, 50)
        ap2_plot.set_data(150, 50)

        # Update each car's position
        for i, car in enumerate(cars):
            x, y, _ = car.getPosition()
            cars_plots[i].set_data(x, y)

        return [ap1_plot, ap2_plot] + cars_plots

    # Set up the animation
    ani = FuncAnimation(fig, update_plot, frames=range(100), interval=500, blit=True)

    # Show the plot in the main thread
    plt.legend()
    plt.show()  # Use plt.show() directly in the main thread

    info("*** Running CLI\n")
    CLI(net)

    info("*** Stopping network\n")
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    topology()
