# coding: utf-8

import select
import time

import xwiimote

N_SENS = 4

# Balance board dimensions in mm (Leach, J.M., Mancini, M., Peterka, R.J., Hayes,
# T.L. and Horak, F.B., 2014. Validating and calibrating the Nintendo Wii
# balance board to derive reliable center of pressure measures. Sensors,
# 14(10), pp.18244-18267.)
BB_Y = 238
BB_X = 433


def format_measurement(x):
    return "{0:.2f}".format(x / 100.0)


def print_bboard_measurements(*args):
    sm = format_measurement(sum(args))
    tl, tr, bl, br = map(format_measurement, args)
    print("\033[H\033[J")
    print("┌","─" * 21, "┐", sep="")
    print("│"," " * 8, "{:>5}".format(sm)," " * 8, "│", sep="")
    print("├","─" * 10, "┬", "─" * 10, "┤", sep="")
    print("│{:^10}│{:^10}│".format(tl, tr))
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
        yield (fl,fr,br,bl)


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


if __name__ == '__main__':
    bb_path = wait4bb()
    dev = xwiimote.iface(bb_path)
    dev.open(xwiimote.IFACE_BALANCE_BOARD)
    for m in measurements(dev):
        print_bboard_measurements(*m)