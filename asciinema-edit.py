# -*- coding: utf-8 -*-
# Copyright 2019 Ross Jacobs All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""🎬 asciicast-edit 🎬

Rearrange and remove sections from asciicasts.

Usage:
  asciicast-edit -r <asciicast> -w <asciicast> [-s <start_ts> <stop_ts>]...
  asciicast-edit -v | --version
  asciicast-edit -h | --help
   
Options:
  -r <asciicast>            Asciicast to read
  -w <asciicast>            Asciicast to which to write
  -s                        Section of session to add to written file
                            The stop timestamp MUST be > start timestamp
                            Sections can be out of order if you want to  
                            rearrange parts of your session
                            
                            To specify an end of file stop ts, use 0
  -h, --help                Print this help
  -v, --version             Print version and exit

Examples:
  https://github.com/pocc/asciinema-edit

  Use rocket.cast from the repo (also at https://asciinema.org/a/238491)
  Let's pretend we like rocket animations, just without the rockets. The rocket
  animation starts at 2.3s and ends at 7s. In order to select everything except
  the section 2.3-7, we will use this command:

  asciicast-edit -r rocket.cast -w no_rocket.cast -s 0 2.3 -s 7 0
  
  The result is no_rocket.cast. It is quite boring without the rocket,
  but there you are.
"""

import json
import re
import sys

import docopt

__version__ = '0.0.1'
# So user can specify end of file
LAST_CAST_TIMESTAMP = 0


def crop(cast_dict, section_tuples):
    """Crop asciicasts with start and stop times

    Structure of asciicast JSON:
    [
        { METADATA JSON },
        [ (Frame 0)
            timestamp (int),
            'o',
            text (str)
        ],
        [ (Frame 1)
        ...
    ]

    Args:
        cast_dict (str): Dict of values from an asciicast
        section_tuples (list): List of start/stop tuples to include

    Returns:
        Modified Asciicast JSON
    """
    validate_sections(section_tuples)
    metadata, data_frames = cast_dict[0], cast_dict[1:]

    # Remove frames not in crop ranges
    new_asciicast = [metadata]
    ts_offset = 0
    for section_index, section in enumerate(section_tuples):
        start_ts, stop_ts = section
        if stop_ts == LAST_CAST_TIMESTAMP:
            stop_ts = data_frames[-1][0]
        for frame in data_frames:
            if stop_ts >= frame[0] >= section[0]:
                # Adjust timestamp by start of time slice
                frame[0] = frame[0] - start_ts + ts_offset
                new_asciicast += [frame]
        ts_offset += stop_ts - start_ts

    return new_asciicast


def validate_sections(sections):
    """Make sure that sections are sane. Validate that there is no overlap."""
    # Sort list of startstop tuples by start time
    sorted_tuples = sorted(sections, key=lambda x: x[0])
    if len(sorted_tuples) < 1:
        raise Exception("Enter at least one set of timestamps like -s 0 5")
    last_value = 0
    num_sections = len(sorted_tuples)

    def print_error_and_exit(message):
        """Print an error message and exit."""
        print("ERROR!", message)
        sys.exit()

    for index, section in enumerate(sorted_tuples):
        if not section[0] >= 0:
            print_error_and_exit("Start timestamps must be > 0!")
            sys.exit()
        if section[1] < 0:
            print_error_and_exit("Stop timestamps must >= 0!")
        if section[1] != 0 and section[1] <= section[0]:
            print_error_and_exit("Stop timestamps must come "
                                 "after start timestamps")
        if section[0] < last_value:
            print_error_and_exit("Section overlap detected!" +
                                 str(section[0]) + str(last_value))
        if section[1] == 0 and index + 1 < num_sections:
            print_error_and_exit("Section overlap detected!"
                                 " Check your use of 0 as a stop timestamp.")
        last_value = section[1]
    

def import_cast(src_file):
    """Take an asciicast file and return a tuple of metadata and frame list"""
    with open(src_file) as cast:
        filetext = cast.read()

    file_json_str = '[' + re.sub(r'([]}])\n\[', '\\1,[', filetext) + ']'
    return json.loads(file_json_str)


def export_cast(dst_file, asciicast_dict):
    """Export the asciicast dict into a file format Asciinema understands."""
    with open(dst_file, 'w') as dest_file:
        dest_file.write(json.dumps(asciicast_dict[0]))
        for data_frame in asciicast_dict[1:]:
            # Get only first 6 digits from mantissa and keep as float
            data_frame[0] = float(format(data_frame[0], 'f'))
            dest_file.write('\n' + json.dumps(data_frame))


def parse_args():
    """Parse args from docopt and return required args."""
    args = docopt.docopt(__doc__)
    if args["--version"]:
        print(__version__)
        sys.exit()
    sections = []
    for i, start in enumerate(args['<start_ts>']):
        stop = args['<stop_ts>'][i]
        sections += [(float(start), float(stop))]
    return args['-r'], args['-w'], sections


def main():
    """Main function."""
    src_file, dst_file, sections = parse_args()
    src_cast_json = import_cast(src_file)
    modified_cast_json = crop(src_cast_json, sections)
    export_cast(dst_file, modified_cast_json)


if __name__ == 'main':
    main()

main()
