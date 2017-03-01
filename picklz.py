import argparse
from liblo import Server
from liblo import UDP
from signal import SIGINT
from signal import SIGTERM
from signal import signal

from bibliopixel import LEDStrip
from bibliopixel import colors
from bibliopixel.drivers.serial_driver import *

from BiblioPixelAnimations.strip import LarsonScanners
from BiblioPixelAnimations.strip import Rainbows
from BiblioPixelAnimations.strip import PartyMode
from BiblioPixelAnimations.strip import FireFlies
from BiblioPixelAnimations.strip import WhiteTwinkle
from BiblioPixelAnimations.strip import Wave
from BiblioPixelAnimations.strip import ColorChase


led = None
current_anim = None
presets = []


def set_off(addr, data, types, client_addr):
    led.all_off()
    led.update()


def set_preset(addr, data, types, client_addr):
    global presets, current_anim
    if current_anim:
        current_anim.stopThread(wait=True)
        current_anim = None
    if len(data) < 2:
        return
    p_num = int(data[0])
    fps = int(data[1])
    if fps <= 0:
        fps = 50
    if p_num < 0 or p_num >= len(presets):
        p_num = 0
    current_anim = presets[p_num]
    current_anim.run(fps=fps, threaded=True)


def sig_exit(sig, frame):
    global led
    print('Exit on signal: %r' % sig)
    led.all_off()
    led.update()
    sys.exit(0)


def main():
    global led, presets

    parser = argparse.ArgumentParser(description='AllPixel OSC controller',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--port', dest='port', default=7676,
                        help='Port to listen on')
    parser.add_argument('--num-leds', dest='num_leds', default=194,
                        help='Number of LEDs on strip')
    args = parser.parse_args()

    signal(SIGINT, sig_exit)
    signal(SIGTERM, sig_exit)

    osc = Server(args.port, UDP)
    osc.add_method("/off", None, set_off)
    osc.add_method("/presets", None, set_preset)

    driver = DriverSerial(type=LEDTYPE.WS2801, num=int(args.num_leds), c_order=ChannelOrder.BGR)
    led = LEDStrip(driver)

    presets += [
        LarsonScanners.LarsonScanner(led, color=colors.Cyan, tail=60),
        LarsonScanners.LarsonRainbow(led, tail=60),
        Rainbows.Rainbow(led),
        PartyMode.PartyMode(led, [colors.White, colors.Blue]),
        FireFlies.FireFlies(led, [colors.Gold, colors.Red], width=12, count=4),
        WhiteTwinkle.WhiteTwinkle(led),
        Wave.Wave(led, color=colors.Cyan, cycles=4),
        ColorChase.ColorChase(led, color=colors.Cyan, width=20)
    ]

    set_preset('', [0, 50], '', '')

    while True:
        osc.recv(100)


if __name__ == '__main__':
    main()
