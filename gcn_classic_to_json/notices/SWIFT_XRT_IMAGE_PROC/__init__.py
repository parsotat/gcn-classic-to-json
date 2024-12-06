from ..SWIFT_XRT_IMAGE import parse_swift_xrt_image


def parse(bin):
    bin[10]  # Spare. According to Docs: '4 bytes for the future'
    return {**parse_swift_xrt_image(bin)}
