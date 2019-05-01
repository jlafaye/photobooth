import logging
import traceback

has_yeelight = False

try:
    import yeelight
    has_yeelight = True
except:
    logging.info('yeelight module loading failed')

LIGHTS = {}

# TODO: remove this
colorsXX = {
        'warm white': (255, 172, 68),
        'pure white': (255, 255, 255),
        'red': (255, 0, 0),
        'blue': (0, 0, 255),
        'green': (0, 255, 0),
        'fuschia': (255, 0, 255),
        'orange': (255, 165, 0),
        'gold': (255, 215, 0)
}

class YeeLight:

    def __init__(self, light_ip):
        self._light_ip = light_ip
        self._bulb = None
        self.initialize()

    def do(self, op, *args):
        try:
            self.initialize()
            op(*args)
        except:
            logging.warn(("Unable to perform light operation: {} "
                " with arguments: {}\n{}").format(op, args, traceback.format_exc()))
            self._bulb = None

    def initialize(self):
        if self._bulb is None:
            self._bulb = yeelight.Bulb(self._light_ip)
            self.do(self._bulb.turn_on)

    def setColor(self, rgb):
        self.do(self._bulb.set_rgb, rgb[0], rgb[1], rgb[2])


def getOrCreateLight(light_ip, module='yeelight'):
    if light_ip not in LIGHTS:
        if module == 'yeelight' and has_yeelight:
            light = YeeLight(light_ip)
            LIGHTS[light_ip] = light
        else:
            logging.warn("Unable to create light, module:{} light_ip:{}".format(light_ip, module))
            return None
    return LIGHTS[light_ip]


if __name__ == '__main__':
    light = getOrCreateLight('192.168.1.39')
    light.setColor((200, 200, 200))
    # light.setColor((0, 0, 0))
