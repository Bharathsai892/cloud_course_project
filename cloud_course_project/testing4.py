#!/usr/bin/python3

from mn_wifi.net import Mininet_wifi
from mininet.node import Controller
from mn_wifi.node import OVSKernelAP
from mininet.link import TCLink
from mininet.log import setLogLevel, info
from mn_wifi.cli import CLI

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

    # Add some helper functions to move cars
    def move_car(car, new_x, new_y):
        car.setPosition('%d,%d,0' % (new_x, new_y))
        net.mobility.set_mp(car)  # Update the plot
        
    # Add the move_car function to the network object for CLI access
    net.move_car = move_car

    info("*** Running CLI\n")
    CLI(net)

    info("*** Stopping network\n")
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    topology()