from ..SWIFT_SC_SLEW import parse_slew


def parse(bin):
    bin[11:13]  # Spare. According to Docs: '8 bytes for the future'
    bin[25:38]  # Spare. According to Docs: '52 bytes for the future'
    bin[19]  # Unused. Flags are either internal or equivalent to bin[16]

    return {**parse_slew(bin)}
