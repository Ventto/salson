#!/usr/bin/env python

import csv
import json
import re
import sys
import os

DEBUG = False

# Standard 8-bit CSV
def i2c_convert_csv_to_json(csv_file, json_file):
    with open(csv_file) as csv_f:
        data = {}
        data['packets'] = []
        line_count = 0
        pkg_idx = 0
        pkt_process = False

        csv_reader = csv.reader(csv_f, delimiter=',')
        for row in csv_reader:
            # Skip the header line
            if line_count == 0:
                line_count += 1
                continue

            operation = re.search('^Setup (Read|Write) to \[0x[0-9A-F]{2}\] \+ ACK',
                                  row[2])
            if operation:
                if pkt_process:
                    pkg_idx += 1
                    pkt_process = False
                addr = re.search('0x[0-9A-F]{2}', row[2])
                data['packets'].append(
                    {
                        'address' : addr.group(0),
                        'operation' : operation.group(1).lower(),
                        'bytes' : {},
                        'metadata' : {}
                    }
                )
            else:
                if re.search('^0x[0-9A-F]{2} \+ (ACK|NAK)', row[2]):
                    byte = re.search('.*(0x[0-9A-F]{2}).*', row[2])
                    if not pkt_process:
                        data['packets'][pkg_idx]['bytes'] = []
                        pkt_process = True
                    data['packets'][pkg_idx]['bytes'].append(
                        {
                            'byte' : byte.group(1),
                            'timestamp' : row[0]
                        }
                    )
                else:
                    print("Error: invalid line")
                    print("Line:", row)
                    sys.exit(3)
            line_count += 1

        if DEBUG:
            print(data)

        with open(json_file, 'w') as outfile:
            json.dump(data, outfile)

def is_readable_file(path):
    try:
        with open(path):
            return True
    except IOError:
        return False

def usage():
    desc = """
This script converts an exported CSV file from Saleae's Logic software for I2C
into a JSON format.

Arguments:

  INPUT_CSV      File path to the INPUT_CSV file.
  OUTPUT_JSON    File path to the OUTPUT_JSON file.
    """
    print("Usage:", os.path.basename(sys.argv[0]), "INPUT_CSV OUTPUT_JSON")
    print(desc)

def main():
    if len(sys.argv) != 3:
        usage()
        sys.exit(2)

    csv_file = sys.argv[1]
    json_file = sys.argv[2]

    if not is_readable_file(csv_file):
        print(csv_file, ": file not found or read-protected")
        sys.exit(1)

    i2c_convert_csv_to_json(csv_file, json_file)

if __name__ == "__main__":
    main()
