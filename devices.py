import serial
import serial.tools.list_ports
from helpers import mod_rtu_crc
import time
from OEM import LDevAbs, BRDCheckStatus
from helpers import LogController
logController = LogController()
device = LDevAbs()

def get_device_list():
    dev_list = []
    try:
        # Serial communication
        ports = serial.tools.list_ports.comports(include_links=False)
        for port in ports:
            try:
                ser = serial.Serial(port.device, baudrate=19200, timeout=1)
                
                # Send request for device ID
                byte_to_send = bytearray([1, 0x01, 0x02, 0x00, 0x00, 0x00])
                byte_to_send.extend(bytearray([(mod_rtu_crc(byte_to_send, 4) >> 8) & 0xFF, mod_rtu_crc(byte_to_send, 4) & 0xFF]))
                
                ser.write(byte_to_send)
                time.sleep(0.02)  # Wait time
                
                byte_to_read = ser.read(12)
                
                if len(byte_to_read) == 12 and \
                (mod_rtu_crc(byte_to_read, len(byte_to_read) - 2) & 0xFF) == byte_to_read[10] and \
                (mod_rtu_crc(byte_to_read, len(byte_to_read) - 2) >> 8) == byte_to_read[11]:
                    dev_list.append(f'{port.device}-OEM-{byte_to_read[4]:X}[SN{byte_to_read[9]:X}{byte_to_read[8]:X}{byte_to_read[7]:X}{byte_to_read[6]:X}]-{byte_to_read[5]:X}')
                else:
                    logController.Write(f"CRC check failed for {port.device}")
                
                ser.close()
                
            except serial.SerialException as e:
                logController.Write(f"Error communicating with {port.device}: {e}")
                message = "Device is in use" if 'Access is denied.' in str(e) else "Failed to list devices"
                return {
                    "status": "FAILED",
                    "output": message
                }
                
        return {
            "status": "SUCCESS",
            "output": dev_list
        }
    except Exception as ex:
        print("Error in listing devices", ex)

