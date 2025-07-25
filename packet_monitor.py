"""
This file is meant to monitor the directory where gromain places the binary 160 byte packets.

It will continually identify new binary packets and convert them to json files which can then be sent out via kafka
"""

import argparse
from pathlib import Path
import logging
import time
import os
import json
from gcn_classic_to_json import notices
from gcn_classic_to_json.json import dumps


def cli():
    parser = argparse.ArgumentParser(description='Process 160 byte binary packets and convert to JSON.')
    parser.add_argument('--datadir', required=True, type=str, help='Directory where the 160 byte packets will be placed')
    parser.add_argument('--logdir', required=True, type=str, help='Directory where the log file will be placed')
    parser.add_argument('--logname', required=False, type=str, default="packet_monitor.log", help='Directory where the log file will be placed')
    parser.add_argument('--send_json', action='store_true',
                        help="This allows for the json notices to be sent via kafka.")

    # parser.add_argument('--tmin', required=False, type=str, help='min time to start')
    # parser.add_argument('--tmax', required=False, type=str, help='max time to start')
    # parser.add_argument('--ext_obsid', required=False, type=str, help='obsid')
    # parser.add_argument('--pipe', required=False, type=str, help='pipeline, either imaging or mosaic')
    # parser.add_argument('--healpix_nside', type=int,\
    #         help="Nside of mosaic healpix map",\
    #         default=256)
    # parser.add_argument('--skyview_nprocs', type=int,\
    #         help="Number of processes to use when creating skyviews in parallel",\
    #         default=8)
    # parser.add_argument('--mosaic_nprocs', type=int,\
    #         help="Number of processes to use when creating mosaic in parallel. NOTE: ALLOCATE ~10GB OF MEMORY PER PROCESS.",\
    #         default=8)
    args = parser.parse_args()
    return args

def convert_notice(binary_path, json_path):

    value = binary_path.read_bytes()
    actual_str = dumps(notices.parse(value), indent=2)

    with json_path.open("w") as f:
        print(actual_str, file=f)
    logging.info(f"Saved converted packet to {json_path}.")


def main(args):
    #go through the arguments
    datadir=Path(args.datadir)
    logdir=Path(args.logdir)

    #do some error checking
    if not datadir.exists():
        raise RuntimeError(f"The data directory {datadir} doesnt exist.")
    if not logdir.exists():
        raise RuntimeError(f"The directory where the log file will be placed, {logdir} doesnt exist.")

    if args.send_json:
        raise NotImplementedError

    #setup the logger
    logging.basicConfig(filename=logdir.joinpath(args.logname), level=logging.DEBUG,
                        format='%(asctime)s - %(levelname)s - %(message)s')

    #print something out
    logging.info(f'packet monitor starting.')
    logging.info(f'The data directory that will be monitored is: {datadir}.')

    #setting sleep_time = 1 second by default. If there is nothing that is happening, we may want to increase this
    sleep_time=1
    logging.info(f"Set sleep_time to {sleep_time} second.")

    #initalize this to false
    was_converted=False

    #now start to do a loop
    while True:
        #look for files in the datadir, sort by time
        binary_packets = sorted(datadir.iterdir(), key=os.path.getmtime, reverse=True)

        #exclude any packets with .json in the name or those that have .json counterparts
        binary_packets=[i for i in binary_packets if "json" not in i.name and not (i.parent.joinpath(f"{i.name}.json").exists())]

        #iterate through the files and produce the json files
        #exclude any binary packets that have already been dealt with. ie they have a name with .json appended
        # these also will be below any packets that are brand new so not super critical
        if len(binary_packets)==0:
            logging.info("No new binary packets were identified to process.")
            sleep_time=60
            logging.info(f"Set sleep_time to {sleep_time} second.")
        else:
            for packet in binary_packets:
                json_conversion_file=packet.parent.joinpath(f"{packet.name}.json")
                if not json_conversion_file.exists():
                    logging.info(f'Packet monitor converting {packet} to json.')

                    #try to do the conversion but catch any errors and print them and move onto the next binary packet.
                    # if we raised an exception in this packet, then dont try to send anything
                    try:
                        convert_notice(packet, json_conversion_file)
                        was_converted=True
                    except Exception as e:
                        logging.debug(e)
                        logging.debug(f"Unable to convert {packet} to json. Moving onto the next packet.")
                        # want to remove a potential json conversion so this packet can be requeued in the
                        # next iteration of the while loop
                        if json_conversion_file.exists():
                            json_conversion_file.unlink()
                            logging.debug(f"File {json_conversion_file} deleted successfully.")
                        else:
                            logging.debug(f"File {json_conversion_file} was not created.")


                    if args.send_json and was_converted:
                        #do something to actually send it off to gcn over kafka
                        raise NotImplementedError

            sleep_time=1
            logging.info(f"Set sleep_time to {sleep_time} second.")

        time.sleep(sleep_time)

    return 0

if __name__ == '__main__':
    args=cli()
    main(args)