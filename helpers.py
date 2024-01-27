import logging
logging.basicConfig(filename='example.log', encoding='utf-8', level=logging.DEBUG)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

class LogController:
    def Write(self, message):
        print(message)
        logging.info(message)

def mod_rtu_crc(buf, length):
        crc = 0xFFFF
        for pos in range(length):
            crc ^= buf[pos]
            for _ in range(8):
                if crc & 0x0001:
                    crc >>= 1
                    crc ^= 0xA001
                else:
                    crc >>= 1
        return crc