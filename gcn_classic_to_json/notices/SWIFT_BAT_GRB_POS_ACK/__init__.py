from astropy.time import Time

# Zero point for Truncated Julian Day according to
# https://en.wikipedia.org/wiki/Julian_day.
TJD0 = (2440000, 0.5)


def parse(bin):
    return dict(
        trigger_time=Time(
            bin[5] + TJD0[0],
            bin[6] / 8640000 + TJD0[1],
            format="jd",
        ).isot,
        ra=1e-4 * bin[7],
        dec=1e-4 * bin[8],
        ra_dec_error=1e-4 * bin[11],
    )
