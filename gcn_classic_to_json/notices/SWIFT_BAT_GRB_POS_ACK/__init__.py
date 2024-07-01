"""
This is a truncated documentation for this packet copied from GCN classic for ease of reference:

TYPE=61 PACKET CONTENTS:

The SWIFT_BAT_GRB_POS_ACK packet consists of 40 four-byte quantities.
The order and contents are listed in the table below:

Declaration  Index   Item         Units           Comments
Type                 Name
-----------  -----   ---------    ----------      ----------------
long         0       pkt_type     integer         Packet type number (=61)
long         1       pkt_sernum   integer         1 thru infinity
long         2       pkt_hop_cnt  integer         Incremented by each node
long         3       pkt_sod      [centi-sec]     (int)(sssss.sss *100)
long         4       trig_obs_num integers        Trigger num & Observation num
long         5       burst_tjd    [days]          Truncated Julian Day
long         6       burst_sod    [centi-sec]     (int)(sssss.sss *100)
long         7       burst_ra     [0.0001-deg]    (int)(0.0 to 359.9999 *10000)
long         8       burst_dec    [0.0001-deg]    (int)(-90.0 to +90.0 *10000)
long         9       burst_flue   [counts]        Num events during trig window, 0 to inf
long         10      burst_ipeak  [cnts*ff]       Counts in image-plane peak, 0 to infinity
long         11      burst_error  [0.0001-deg]    (int)(0.0 to 180.0 *10000)
long         12      phi          [centi-deg]     (int)(0.0 to 359.9999 *100)
long         13      theta        [centi-deg]     (int)(0.0 to +70.0 *100)
long         14      integ_time   [4mSec]         Duration of the trigger interval, 1 to inf
long         15      spare        integer         4 bytes for the future
long         16      lon_lat      2_shorts        (int)(Longitude,Lattitude *100)
long         17      trig_index   integer         Rate_Trigger index
long         18      soln_status  bits            Type of source/trigger found
long         19      misc         bits            Misc stuff packed in here
long         20      image_signif [centi-sigma]   (int)(sig2noise *100)
long         21      rate_signif  [centi-sigma]   (int)(sig2noise *100)
long         22      bkg_flue     [counts]        Num events during the bkg interval, 0 to inf
long         23      bkg_start    [centi-sec]     (int)(sssss.sss *100)
long         24      bkg_dur      [centi-sec]     (int)(0-80,000 *100)
long         25      cat_num      integer         On-board cat match ID number
long         26-35   spare[10]    integer         40 bytes for the future
long         36      merit_0-3    integers        Merit params 0,1,2,3 (-127 to +127)
long         37      merit_4-7    integers        Merit params 4,5,6,7 (-127 to +127)
long         38      merit_8-9    integers        Merit params 8,9     (-127 to +127)
long         39      pkt_term     integer         Pkt Termination (always = \n)
"""

from astropy.time import Time

#set constants for ease of use

# Zero point for Truncated Julian Day according to
# https://en.wikipedia.org/wiki/Julian_day.
TJD0 = (2440000, 0.5)

mission="Swift"
instrument="BAT" #insert instrument here for appropriate notice type


def parse(bin):
    
    solution_bits=f"{bin[18]:032b}"
    merit_bits_03=f"{bin[36]:032b}"
    merit_bits_47=f"{bin[37]:032b}"
    merit_bits_89=f"{bin[38]:032b}"
    misc_bits=f"{bin[19]:032b}"
    
    trig_dur=bin[14]*4/1000
    image_duration=None
    rate_duration=None
    if int(solution_bits[4])==1:
        trig_type="image"
        image_duration=trig_dur
        rate_duration=None
    else:
        trig_type="rate"
        image_duration=None
        rate_duration=trig_dur
    

    packet_dict=dict(
        mission=mission,
        instrument=instrument,
        trigger_time=Time(
            bin[5] + TJD0[0],
            bin[6] / 8640000 + TJD0[1],
            format="jd",
        ).isot,
        id=int(bin[4]),
        ra=1e-4 * bin[7],
        dec=1e-4 * bin[8],
        ra_dec_error=1e-4 * bin[11],
        instrument_phi=bin[12]/100,
        instrument_theta=bin[13]/100,
        latitude=int(f"{bin[16]:032b}"[:16],2)/100 ,
        longitude=int(hex(bin[16]  & 0xffff),16)/100, 
        image_snr=bin[20]/100,
        rate_snr=bin[21]/100,
        rate_duration=rate_duration,
        image_duration=image_duration,
        trigger_type=trig_type,
        rate_energy_range=None,
        image_energy_range=None
    )
    return packet_dict
