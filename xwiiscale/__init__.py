# coding: utf-8

import select
import xwiimote


if __name__ == '__main__':
    p = select.poll()
    mon = xwiimote.monitor(True, False)
    scale_path = mon.poll()
    dev = xwiimote.iface(scale_path)
    dev.open(xwiimote.IFACE_BALANCE_BOARD)
    p.register(dev.get_fd(), select.POLLIN)
    #mon_fd = mon.get_fd(False)
    #p.register(mon_fd, select.POLLIN)
    evt = xwiimote.event()
    #p.poll()
    #dev.dispatch(evt)
    while True:
        p.poll()
        dev.dispatch(evt)
        for i in range(4):
            print('sensor {i}: {val}'.format(i=i, val=evt.get_abs(i)[0]))