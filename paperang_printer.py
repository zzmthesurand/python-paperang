import config
import hardware
import image_data
import skimage as ski
from skimage import transform as skt
import numpy as np
import time

class Paperang_Printer:
    def __init__(self):
        if hasattr(config, "macaddress"):
            print("attempting test print to MAC address \"% s\""% config.macaddress)
            self.printer_hardware = hardware.Paperang(config.macaddress)
        else:
            print("searching for printer for test print...")
            self.printer_hardware = hardware.Paperang()
        if self.printer_hardware.connected:
            print("Connected!")
            #self.printer_hardware.sendFeedToHeadLineToBt(50)
        else:
            print("Not connected!")
        print("Querying stuff")

    def print_self_test(self) -> None:
        print("attempting test print to MAC address \"% s\""% config.macaddress)
        if self.printer_hardware.connected:
            self.printer_hardware.sendSelfTestToBt()

    def print_image_file(self, path, padding=12, density: int = -1, rotation=0) -> None:
        if self.printer_hardware.connected:
            if density >= 0:
                self.printer_hardware.sendDensityToBt(density)
            self.printer_hardware.sendImageToBt(image_data.binimage2bitstream(
                                                    image_data.im2binimage(
                                                        skt.rotate(ski.io.imread(path), 
                                                                    rotation, 
                                                                    resize=True, 
                                                                    order=0, 
                                                                    mode="constant",       # fill outside with constant
                                                                    cval=255,              # 255 = white for uint8
                                                                    preserve_range=True).astype(np.uint8),
                                                    conversion="threshold"
                                                    )))
            self.printer_hardware.sendFeedLineToBt(padding)
            print(self.printer_hardware.queryHardwareInfo())
        else:
            print("Printer is not connected.")
    
    def print_dithered_image(self, path, padding=12) -> None:
        if self.printer_hardware.connected:
            self.printer_hardware.sendImageToBt(image_data.im2binimage2(path))
            self.printer_hardware.sendFeedLineToBt(padding)