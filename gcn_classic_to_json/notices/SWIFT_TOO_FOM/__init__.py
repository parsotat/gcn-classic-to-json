from ..SWIFT_FOM_OBS import parse_fom


def parse(bin):
    bin[11:15]  # Spare. According to Docs: '16 bytes for the future'
    bin[22:38]  # Spare. According to Docs: '64 bytes for the future'
    bin[19]  # Unused. Flags are either internal or equivalent to bin[16]

    return {**parse_fom(bin)}
