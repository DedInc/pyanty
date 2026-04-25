"""CRC helpers for the pure-Python Snappy reader."""


def make_crc_table(poly):
    table = []
    for i in range(256):
        crc = 0
        for _ in range(8):
            if (i ^ crc) & 1:
                crc = (crc >> 1) ^ poly
            else:
                crc >>= 1
            i >>= 1
        table.append(crc)
    return table


CRC_POLY = 0x82F63B78
CRC_QUICK_TABLE = tuple(make_crc_table(CRC_POLY))


def crc32c(data, xor_value=0xFFFFFFFF):
    value = 0xFFFFFFFF
    for b in data:
        value = CRC_QUICK_TABLE[(b ^ value) & 0xFF] ^ (value >> 8)

    value ^= xor_value
    return value


def check_masked_crc(crc, data, xor_value=0xFFFFFFFF):
    check = crc32c(data, xor_value=xor_value)

    check = ((check >> 15) | (check << 17)) & 0xFFFFFFFF  # rotate
    check += 0xA282EAD8  # add constant
    check %= 0x100000000  # wraparound as an uint32

    return crc == check
