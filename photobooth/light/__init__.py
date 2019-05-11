import logging
import traceback

from .. import StateMachine
from ..Threading import Workers

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

class Light:

    def __init__(self, config, comm):
        super().__init__()

        self._comm = comm
        self._colors = []
        self._light = None

        self._is_enabled = config.getBool('PoseSetup', 'enable')

        self.initLight(config)

    def initLight(self, config):
        
        if self._is_enabled:

            # colors
            for n in range(10):
                color_name = config.get('PoseSetup', 'color_name_{}'.format(n))
                color_rgb = config.get('PoseSetup', 'color_rgb_{}'.format(n))
                if not color_name or not color_rgb:
                    continue
                self._colors.append((color_name,
                                    list(map(int, color_rgb.split(',')))))

            module = config.get('PoseSetup', 'module')
            light_ip = config.get('PoseSetup', 'light_ip')

            if module == 'yeelight' and has_yeelight:
                self._light = YeeLight(light_ip)
            else:
                logging.warn("Unable to create light, module:{} light_ip:{}".format(light_ip, module))



    def startup(self):
        self._light.initialize()
        self._light.turnOn()

    def teardown(self):
        self._light.turnOff()

    def run(self):

        for state in self._comm.iter(Workers.LIGHT):
            self.handleState(state)

        return True

    def handleState(self, state):
        if isinstance(state, StateMachine.StartupState):
            self.startup()
        elif isinstance(state, StateMachine.GreeterState):
            color_pos = state._light_color % len(self._colors)
            color_name, color_rgb = self._colors[color_pos]
            self._light.turnOn()
            self._light.setColor(color_rgb)
        elif isinstance(state, StateMachine.IdleState):
            self._light.turnOff()
        elif isinstance(state, StateMachine.TeardownState):
            self.teardown()
        # TODO: implement retro feedback to GUI once the color has changed

class YeeLight:

    def __init__(self, light_ip):
        self._light_ip = light_ip
        self._bulb = None

    def do(self, op, *args):
        logging.info("Calling op: {}".format(op))
        try:
            op(*args)
        except:
            logging.warn(("Unable to perform light operation: {} "
                " with arguments: {}\n{}").format(op, args, traceback.format_exc()))
            self._bulb = None
            self.initialize()

    def initialize(self):
        logging.info('initializing {}'.format(self._light_ip))
        if self._bulb is None:
            self._bulb = yeelight.Bulb(self._light_ip)

    def turnOn(self):
        self.do(self._bulb.turn_on)

    def turnOff(self):
        self.do(self._bulb.turn_off)

    def setColor(self, rgb):
        logging.info('setColor rgb={}'.format(rgb))
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
