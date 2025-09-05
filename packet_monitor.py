"""
This file is meant to monitor the directory where gromain places the binary 160 byte packets.

It will continually identify new binary packets and convert them to json files which can then be sent out via kafka
"""

import argparse
from pathlib import Path
import logging
import time
import os
import regex
import json
import base64
import subprocess
import numpy as np
from gcn import NoticeType
from gcn_classic_to_json import notices
from gcn_classic_to_json.json import dumps


import signal

def handler(signum, frame):
    logging.info(f'Packet_monitor is exiting due to SIGINT.')
    print(f'Packet_monitor is exiting due to SIGINT.')
    exit(0)

signal.signal(signal.SIGINT, handler)


def cli():
    parser = argparse.ArgumentParser(description='Process 160 byte binary packets and convert to JSON.')
    parser.add_argument('--datadir', required=True, type=str, help='Directory where the 160 byte packets will be placed')
    parser.add_argument('--logdir', required=True, type=str, help='Directory where the log file will be placed')
    parser.add_argument('--gromain_logdir', required=True, type=str, help='Directory where the gromain log files will be placed')
    parser.add_argument('--logname', required=False, type=str, default="packet_monitor.log", help='Directory where the log file will be placed')
    parser.add_argument('--send_json', action='store_true',
                        help="This allows for the json notices to be sent via kafka.")
    parser.add_argument('--delta_t_max', required=False, type=int, default=60, help='Maximum amount of time to sleep in seconds between checking the datadir for new binary packets to convert to JSON')


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

def convert_notice(binary_path, json_path, gromain_log):

    value = binary_path.read_bytes()
    parsed_dict=notices.parse(value)

    #after parsing the binary notices, we need to determine if there are attachments that need to be encoded in the json
    if "url" in parsed_dict.keys() or "fits_file_url" in parsed_dict.keys():
        email_script=get_tmp_email_script(binary_path, gromain_log)
        attachments=get_email_attachments(email_script)
        attach_files(parsed_dict, attachments)
        logging.info(f"Done attaching files for the notice.")


    actual_str = dumps(parsed_dict, indent=2)

    with json_path.open("w") as f:
        print(actual_str, file=f)
    logging.info(f"Saved converted packet to {json_path}.")

def attach_files(binary_dict, attachment_list):

    #remove the filename attachment
    if "url" in binary_dict.keys():
        #binary_dict.pop("url")
        logging.debug(f'In attach_files, the url from the dict is: {binary_dict["url"]}')
    elif "fits_file_url" in binary_dict.keys():
        #binary_dict.pop("fits_file_url")
        logging.debug(f'In attach_files, the url from the dict is: {binary_dict["fits_file_url"]}')
    else:
        logging.debug(f"In attach_files, but somehow cannot remove the url from the dict: {binary_dict}")
        raise KeyError(f"In attach_files, but somehow cannot remove url from the dict: {binary_dict}")

    #add a new key to hold a dict with the fits files attachments
    binary_dict["data"]={}

    # iterate through the list of attachments and read them into the binary dict
    for attachment in attachment_list:
        logging.debug(f"Encoding attachment {attachment}.")
        with open(attachment, "rb") as file:
            binary_dict["data"][f"{attachment.name}"] = base64.b64encode(file.read()).decode("utf-8")


def get_tmp_email_script(binary_path, gromain_log):
    """
    want to search the gromain log for where the binary_path is printed and then extract the tmp email script filename
    which has the mail commands used to send the notice.
    """

    # Construct the command with flexible parameters. searching for this line:
    # DBG: distribute(): Unique email script fname is: ...
    command = f'tac {gromain_log} |sed \'/{binary_path.name}/q\' | tac | grep "email script" |head -n 1'

    logging.info(f"Looking for the temporary email script within the Gromain log. Executing command: {command}")


    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            check=True
        )

        logging.info("Command executed successfully")
        logging.debug(f"The line that specifies the tmp email file is: {result.stdout.strip()}")

        match=regex.search(".*:\s+(.*)", result.stdout.strip())
        if match:
            tmp_email_file = Path(match.group(1))
            logging.info(f"Extracted the tmp email file as: {tmp_email_file}")
        else:
            tmp_email_file = None
            logging.info("The regex was not able to extract the tmp email file.")

        return tmp_email_file

    except subprocess.CalledProcessError as e:
        logging.debug(f"Command failed with return code {e.returncode}")

    except Exception as e:
        logging.debug(f"Unexpected error: {str(e)}")


def get_email_attachments(email_script):
    """
    We want to parse the email script to get all the attachments that we eventually need to include in the json notice
    """

    attachment_regex="-a\s+(.*)\s+--"

    with open(email_script, 'r') as file:
        filetext = file.read()

    match = regex.search(attachment_regex, filetext)

    if match:
        all_attachments=match.group(1).split()
        logging.info(f"Identified {len(all_attachments)} attachments associated with the notice:")
        logging.info(f"{', '.join(all_attachments)}")
        attachments=[Path(i) for i in all_attachments]

        #make sure that all the attachments exist
        for i in attachments:
            if not i.exists():
                logging.debug(f"The attachment {i} for this notice doesnt seem to exist.")
                raise RuntimeError(f"The attachment {i} for this notice doesnt seem to exist.")

    else:
        logging.debug(f"No attachments were associated with the notice.")
        raise RuntimeError(f"No attachments were associated with the notice.")
        attachments=None

    return attachments



def select_gromain_log(gromain_logdir):
    logs = sorted(gromain_logdir.iterdir(), key=os.path.getmtime, reverse=False)

    # exclude non-gromain logs
    gromain_logs = [i for i in logs if "G" in i.name]

    if len(gromain_logs) <1:
        raise RuntimeError(f"There seem to be no gromain logs in the directory {gromain_logdir}.")

    #select the latest one
    return gromain_logs[-1]


def main(args):
    #go through the arguments
    datadir=Path(args.datadir)
    logdir=Path(args.logdir)
    gromain_logdir=Path(args.gromain_logdir)
    max_t=args.delta_t_max

    #do some error checking
    if not datadir.exists():
        raise RuntimeError(f"The data directory {datadir} doesnt exist.")
    if not logdir.exists():
        raise RuntimeError(f"The directory where the log file will be placed, {logdir} doesnt exist.")
    if not gromain_logdir.exists():
        raise RuntimeError(f"The gromain log directory {gromain_logdir} doesnt exist.")

    #get the gromain logname
    gromain_log=select_gromain_log(gromain_logdir)

    if not gromain_log.exists():
        raise RuntimeError(f"The gromain log  {gromain_log} doesnt exist.")



    if args.send_json:
        raise NotImplementedError

    #setup the logger
    logging.basicConfig(filename=logdir.joinpath(args.logname), level=logging.DEBUG,
                        format='%(asctime)s.%(msecs)03d - %(levelname)s - %(message)s', datefmt="%Y-%m-%dT%H:%M:%S")
    #use UTC time
    logging.Formatter.converter = time.gmtime

    #print something out
    logging.info(f'packet monitor starting.')
    logging.info(f'The data directory that will be monitored is: {datadir}.')
    logging.info(f'The gromain log that is being monitored is: {gromain_log}')

    #setting sleep_time = 1 second by default. If there is nothing that is happening, we may want to increase this
    sleep_time=1
    logging.info(f"Set sleep_time to {sleep_time} second.")

    #initalize this to false
    was_converted=False

    #now start to do a loop
    while True:
        #look for files in the datadir, sort by time
        binary_packets = sorted(datadir.iterdir(), key=os.path.getmtime, reverse=False)

        #exclude non-swift binary packets, see save_swift function in hete.c
        binary_packets = [i for i in binary_packets if "S" in i.name]

        #exclude any packets with .json in the name or those that have .json counterparts
        binary_packets=[i for i in binary_packets if "json" not in i.name and not (i.parent.joinpath(f"{i.name}.json").exists())]

        #exclude any packets that dont have a counterpart in the gcn NoticeTypes, need to loop over 2 things which isnt great
        #first extrac the packet type and then compare them to the gcn NoticeTypes
        binary_packet_num=[np.frombuffer(i.read_bytes(), dtype="<i4")[0] for i in binary_packets]
        binary_packets=[i for i,pkt_num in zip(binary_packets,binary_packet_num) for j in NoticeType if j.value == pkt_num]

        #iterate through the files and produce the json files
        #exclude any binary packets that have already been dealt with. ie they have a name with .json appended
        # these also will be below any packets that are brand new so not super critical
        if len(binary_packets)==0:
            logging.info("No new binary packets were identified to process.")
            if sleep_time < max_t:
                sleep_time+=1
                logging.info(f"Set sleep_time to {sleep_time} seconds.")
            logging.info(f"Sleeping for {sleep_time} seconds.")
        else:
            #need to make sure that the gromain log hasnt changed due to eg a new day so a new log being created
            # to prevent iterating over the log directory too much, try to do this when we think we need it done
            new_gromain_logname = f'G{time.strftime("%y%m%d", time.gmtime())}.log'
            if new_gromain_logname != gromain_log.name:
                gromain_log=select_gromain_log(gromain_logdir)
                logging.info(f'The gromain log that is being monitored has changed it is now: {gromain_log}')

                #this shouldnt ever execute due to how we are selecting the file directly from the directory, but this
                # is here just in case
                if not gromain_log.exists():
                    logging.debug(f"The gromain log  {gromain_log} doesnt exist.")
                    raise RuntimeError(f"The gromain log  {gromain_log} doesnt exist.")

            for packet in binary_packets:
                json_conversion_file=packet.parent.joinpath(f"{packet.name}.json")
                if not json_conversion_file.exists():
                    logging.info(f'Packet monitor converting {packet} to json.')

                    #try to do the conversion but catch any errors and print them and move onto the next binary packet.
                    # if we raised an exception in this packet, then dont try to send anything
                    try:
                        convert_notice(packet, json_conversion_file, gromain_log)
                        was_converted=True
                    except Exception as e:
                        logging.debug(f"{type(e).__name__} Exception raised with message: {e}")
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
