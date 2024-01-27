import serial
import time
from enum import Enum
from helpers import LogController, mod_rtu_crc

class BRDCheckStatus(Enum):
    Warming = 0
    Ready = 1
    Busy = 2
    Overload = 3
    Error = 4

logController = LogController()

class LDevAbs:
    
    def __init__(self):
        self.m_ErrorMessage = ""
        self.m_SerialPort = serial.Serial()

    def Initialize(self, comAddress):
        
        info = comAddress.split('-')
        logController.Write("RUN INIT OEM")
        self.m_ErrorMessage = ""

        try:
            
            if not self.m_SerialPort.is_open:
                self.m_SerialPort.port = info[0]
                self.m_SerialPort.bytesize = 8
                self.m_SerialPort.baudrate = 19200
                # self.m_SerialPort.parity = serial.Parity.NONE
                self.m_SerialPort.stopbits = 1
                self.m_SerialPort.timeout = 1

                self.m_SerialPort.open()

                logController.Write("END RUNNING INIT OEM")
                return True
            
            # self.m_ErrorMessage = f"Er004: Port {comAddress} already in use"
            # logController.Write("END RUNNING INIT OEM")
            # return False
        except Exception as ex:
            print(f"Er099= Device ComPort Initialize Function Error {ex}")
            self.m_ErrorMessage = f"Er099= Device ComPort Initialize Function Error {ex}"
            # logController.Write("Exception:END RUNNING INIT OEM")
            return False

    def Close(self):
        self.m_ErrorMessage = ""

        try:
            if self.m_SerialPort.is_open:
                self.m_SerialPort.close()
            return True
        except Exception as ex:
            self.m_ErrorMessage = f"Er099= Close ComPort Function Error {ex}"
            return False

    def InputValidate(self, startV, stopV, stepV, sweepDelayms):
        try:
            self.m_ErrorMessage = ""
            logController.Write("Check Input Arguments")

            if not (0 <= startV <= 3000) or not (0 <= stopV <= 3000):
                self.m_ErrorMessage = "Er005= Voltage Set Out of Range, Available Range 0-3V"
                return False

            if not (0 <= stepV <= 3000):
                self.m_ErrorMessage = "Er006= Voltage Step Out of Range, Available Step Range 0-3V"
                return False

            if not (100 <= sweepDelayms <= 1000):
                self.m_ErrorMessage = "Er007= Sweep Delay out of Range, Available Range is 100ms - 1000ms"
                return False

            return True
        except Exception as ex:
            self.m_ErrorMessage = f"Er099= Device InputValidate Function Error {ex}"
            logController.Write("END RUNNING ZERO_CHECK OEM")
            return False

    def CheckStatus(self):
        try:
            logController.Write("RUN CHECKSTATUS OEM")
            invalid_count = 0

            while invalid_count < 2:
                self.m_ErrorMessage = ""
                _ByteToSend = bytearray([1, 0x02, 0x02, 0x00, 170, 170])
                self.m_SerialPort.write(_ByteToSend)
                logController.Write(">> " + " ".join(format(x, '02X') for x in _ByteToSend))

                for _ in range(10):
                    time.sleep(0.02)
                    if self.m_SerialPort.in_waiting >= 7:
                        break

                _ByteToRead = bytearray(self.m_SerialPort.read(self.m_SerialPort.in_waiting))
                logController.Write("<< " + " ".join(format(x, '02X') for x in _ByteToRead))

                if len(_ByteToRead) == 7:
                    crc_low = (mod_rtu_crc(_ByteToRead, len(_ByteToRead) - 2) & 0x00FF)
                    crc_high = (mod_rtu_crc(_ByteToRead, len(_ByteToRead) - 2) >> 8)

                    if crc_low == _ByteToRead[5] and crc_high == _ByteToRead[6]:
                        status = _ByteToRead[4]

                        if status == 0:
                            self.m_ErrorMessage = "Device Warming Up"
                            return BRDCheckStatus.Warming
                        elif status == 1:
                            self.m_ErrorMessage = "Device Ready"
                            return BRDCheckStatus.Ready
                        elif status == 2:
                            self.m_ErrorMessage = "Device On Busy"
                            return BRDCheckStatus.Busy
                        elif status == 3:
                            self.m_ErrorMessage = "Device Overload"
                            return BRDCheckStatus.Overload
                        else:
                            self.m_ErrorMessage = "Device Error"
                            return BRDCheckStatus.Error
                    else:
                        self.m_ErrorMessage = "Er009: CRC check fail for CheckStatus"
                        invalid_count += 1
                        time.sleep(0.1)
                else:
                    self.m_ErrorMessage = "Er010: Response length error for CheckStatus"
                    invalid_count += 1
                    time.sleep(0.1)

            logController.Write("Er011= CheckStatus Failed")
            return BRDCheckStatus.Error

        except Exception as ex:
            self.m_ErrorMessage = f"Er099= Device CheckStatus Function Error {ex}"
            logController.Write("END RUNNING ZERO_CHECK OEM")
            return BRDCheckStatus.Error



