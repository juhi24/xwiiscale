# coding: utf-8

import select
import time
import threading

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation
import matplotlib as mpl

import xwiimote

N_SENS = 4

# Balance board dimensions in mm (Leach, J.M., Mancini, M., Peterka, R.J., Hayes,
# T.L. and Horak, F.B., 2014. Validating and calibrating the Nintendo Wii
# balance board to derive reliable center of pressure measures. Sensors,
# 14(10), pp.18244-18267.)
BB_Y = 238
BB_X = 433


class BalanceMeter(threading.Thread):
    def __init__(self, devpath):
        super().__init__()
        self.dev = xwiimote.iface(devpath)
        self.dev.open(xwiimote.IFACE_BALANCE_BOARD)
        self.p = select.epoll.fromfd(self.dev.get_fd())
        self.m = None
        self.run_flag = True

    def run(self):
        while self.run_flag:
            self.p.poll()
            event = xwiimote.event()
            self.dev.dispatch(event)
            #  0,  1,  2,  3
            # FR, BR, FL, BL
            self.m = np.array([event.get_abs(i)[0] for i in range(N_SENS)])

    def xy(self):
        fr, br, fl, bl = self.m
        x = fr + br - fl - bl
        y = fl + fr - bl - br
        return x, y


def format_measurement(x):
    return "{0:.2f}".format(x / 100.0)


def print_bboard_measurements(*args):
    sm = format_measurement(sum(args))
    fl, fr, bl, br = map(format_measurement, args)
    print("\033[H\033[J")
    print("┌","─" * 21, "┐", sep="")
    print("│"," " * 8, "{:>5}".format(sm)," " * 8, "│", sep="")
    print("├","─" * 10, "┬", "─" * 10, "┤", sep="")
    print("│{:^10}│{:^10}│".format(fl, fr))
    print("│"," " * 10, "│", " " * 10, "│", sep="")
    print("│"," " * 10, "│", " " * 10, "│", sep="")
    print("│{:^10}│{:^10}│".format(bl, br))
    print("└","─" * 10, "┴", "─" * 10, "┘", sep="")


def measurements(dev):
    p = select.epoll.fromfd(dev.get_fd())
    while True:
        p.poll() # blocks
        event = xwiimote.event()
        dev.dispatch(event)
        fl = event.get_abs(2)[0]
        fr = event.get_abs(0)[0]
        br = event.get_abs(3)[0]
        bl = event.get_abs(1)[0]
        yield fl, fr, br, bl


def dev_is_balanceboard(devpath):
    time.sleep(0.5) # too early check is reported as 'unknown'
    iface = xwiimote.iface(devpath)
    return iface.get_devtype() == 'balanceboard'


def wait4bb():
    """Wait for balance board."""
    print("Waiting for balance board to connect.")
    mon = xwiimote.monitor(True, False)
    devpath = None
    while True:
        mon.get_fd(True) # blocks
        connected = mon.poll()
        if connected == None:
            continue
        elif dev_is_balanceboard(connected):
            print("Found balanceboard:", connected)
            devpath = connected
            break
        else:
            print("Found non-balanceboard device:", connected)
            print("Still waiting...")
    return devpath


def cop_vector(dev):
    for fl, fr, br, bl in measurements(dev):
        x = fr + br - fl - bl
        y = fl + fr - br - bl
        yield x, y


if __name__ == '__main__':
    bb_path = wait4bb()
    bb = BalanceMeter(bb_path)
    fig, ax = plt.subplots()
    ax.set_ylim(bottom=-2000, top=2000)
    ax.set_xlim(left=-2000, right=2000)
    bb.start()
    ln, = plt.plot([], [], 'bo')
    def update(xy):
        ln.set_data([xy[0]], [xy[1]])
    def frames():
        while True:
            yield bb.xy()
    anim = animation.FuncAnimation(fig, update, frames=frames, interval=100)
#    for m in measurements(dev):
#        print_bboard_measurements(*m)
#    for xy in cop_vector(dev):
#        print(*xy)