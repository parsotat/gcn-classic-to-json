from ..SWIFT_UVOT_DBURST_PROC import parse_uvot_image


def parse(bin):
    bin[
        18
    ]  # Unused. According to Docs: 'useless by the time it reaches GCN distribution'
    bin[20:22]  # Spare. According to Docs: '8 bytes for the future'

    return {**parse_uvot_image(bin)}
