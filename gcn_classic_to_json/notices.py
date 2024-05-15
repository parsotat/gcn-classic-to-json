"""
Translation from binary formats to JSON.

See https://gcn.gsfc.nasa.gov/sock_pkt_def_doc.html,
https://github.com/nasa-gcn/gcn-schema
"""


def SWIFT_BAT_GRB_POS_ACK(bin):
    return dict(ra=1e4 * bin[7], dec=1e4 * bin[8])
