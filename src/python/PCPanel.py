import hid
import pactl
from collections import defaultdict


def find_device():
# Enumerar todos los dispositivos HID conectados
    devices = hid.enumerate()

    # Imprimir información de cada dispositivo
    for device_info in devices:
        if (device_info["manufacturer_string"] == "PCPanel Holdings LLC"):
            print("Device Found:")
            print("  Path:", device_info["path"])
            print("  Vendor ID:", hex(device_info["vendor_id"]))
            print("  Product ID:", hex(device_info["product_id"]))
            print("  Serial Number:", device_info["serial_number"])
            print("  Manufacturer:", device_info["manufacturer_string"])
            print("  Product:", device_info["product_string"])
            print("  Release Number:", device_info["release_number"])
            print("  Interface Number:", device_info["interface_number"])
            print()

            return device_info["vendor_id"], device_info["product_id"]

    # Si no se encuentra ningún dispositivo
    return None, None

class PCPanel:
    def __init__(self, inputs = {}):
        self.pcpanel = hid.device()
        vendor_id, product_id = find_device()
        self.pcpanel.open(vendor_id, product_id)
        self.pcpanel.set_nonblocking(1)
        self.K1 = input(*inputs.get('K1', None)) 
        self.B1 = input(*inputs.get('B1', None)) 
        self.K2 = input(*inputs.get('K2', None)) 
        self.B2 = input(*inputs.get('B2', None)) 
        self.K3 = input(*inputs.get('K3', None)) 
        self.B3 = input(*inputs.get('B3', None)) 
        self.K4 = input(*inputs.get('K4', None)) 
        self.B4 = input(*inputs.get('B4', None)) 
        self.K5 = input(*inputs.get('K5', None)) 
        self.B5 = input(*inputs.get('B5', None)) 
        self.S1 = input(*inputs.get('S1', None)) 
        self.S2 = input(*inputs.get('S2', None)) 
        self.S3 = input(*inputs.get('S3', None)) 
        self.S4 = input(*inputs.get('S4', None)) 
        self.widgets = {
                1: {0: self.K1,
                    1: self.K2,
                    2: self.K3,
                    3: self.K4,
                    4: self.K5,
                    5: self.S1,
                    6: self.S2,
                    7: self.S3,
                    8: self.S4,
                    },
                2: {0: self.B1,
                    1: self.B2,
                    2: self.B3,
                    3: self.B4,
                    4: self.B5}
                }
    

    def __del__(self):
        self.pcpanel.close()
    

    def _data(self):
        data = []
        try: 
            data = self.pcpanel.read(3,250)
        except IOError as ex:
            print(ex)
        return data
    

    def loop(self):
        data = self._data()
        
        if not data:
            return
        
        try:
            if (data[0] == 1):      # slider/knob
                self.widgets.get(1).get(data[1]).adjust(data[2])
            elif (data[0] == 2):    # button
                self.widgets.get(2).get(data[1]).press(data[2])
        except TypeError as ex:
            raise


class input:
    """
    TODO
    - auto release (unmute after 10 sec, etc)
    """
    def __init__(self, apps = [], devs = [], active = False, default_sink = False, default_source = False):
        self.apps = apps
        self.devs = devs
        self.active = active
        self.min = 0
        self.max = 100
        self.log = False
        self.default_sink = default_sink
        self.default_source = default_source
 

    def loop_apps(self, val):
        try:
            for app in self.apps:
                for iden in pactl.dict_apps().get(app):
                    pactl.sink_input_vol(iden, val)
        except KeyError:
            pass
        except TypeError:
            pass
    

    def loop_devs(self, val):
        try:
            for dev in self.devs:
                pass
        except KeyError:
            raise
        except TypeError:
            pass


    def loop_apps_mute(self, action = 'toggle'):
        try:
            for app in self.apps:
                for iden in pactl.dict_apps().get(app):
                    pactl.sink_input_mute(iden, action)
        except KeyError:
            pass
        except TypeError:
            pass


    def loop_devs_mute(self, action = 'toggle'):
        try:
            for app in self.devs:
                pass
        except KeyError:
            pass
        except TypeError:
            pass
        

    def adjust(self, val):
        if self.log:
            # do things to val
            pass
        else:
            val = int(val/255*100)
        if self.active:
            pactl.active_sink_input_vol(val)
        self.loop_apps(val)
        self.loop_devs(val)

        
    def press(self, state, last_pressed = False):
        if state:
            self.loop_apps_mute()
            self.loop_devs_mute()
            if self.default_sink:
                pactl.sink_default_mute()
            if self.default_source:
                pactl.source_default_mute()


    def double_press(self):
        pass
    

    def hold(self):
        pass
