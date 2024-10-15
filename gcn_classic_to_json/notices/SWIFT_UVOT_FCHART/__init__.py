from ..SWIFT_UVOT_FCHART_PROC import parse_uvot_srclist


def parse(bin):
    bin[19]  # Intentionally Omitted. Bits seemed to be used for internal messages
    bin[20:22]  # Spare. According to Docs: '8 bytes for future use'

    return {**parse_uvot_srclist(bin)}
