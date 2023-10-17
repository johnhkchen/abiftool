#!/usr/bin/env python3
# abiftool.py - conversion to/from .abif to other electoral expressions
#
# Copyright (C) 2023 Rob Lanphier
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from abiflib import *
import argparse
import json
import os
import re
import sys
import urllib.parse

INPUT_FORMATS = ['abif', 'debtally', 'jabmod', 'preflib', 'widj']

OUTPUT_FORMATS = ['abif', 'html', 'html_snippet', 'jabmod',
                  'paircountjson', 'texttable', 'texttablecountsonly',
                  'winlosstiejson']

ABIF_VERSION = "0.1"
ABIFMODEL_LIMIT = 2500
LOOPLIMIT = 400

def main():
    """Convert between .abif-adjacent formats."""
    parser = argparse.ArgumentParser(
        description='Convert between .abif and JSON formats')
    parser.add_argument('input_file', help='Input file to convert')
    parser.add_argument('-t', '--to', choices=OUTPUT_FORMATS,
                        required=True, help='Output format')
    parser.add_argument('-f', '--fromfmt', choices=INPUT_FORMATS,
                        help='Input format (overrides file extension)')

    args = parser.parse_args()

    # Determine input format based on file extension or override from
    # the "-f/--fromfmt" option
    if args.fromfmt:
        input_format = args.fromfmt
    elif args.input_file == '-':
        parser.error("The -f parameter is required with '-'")
    else:
        _, file_extension = args.input_file.rsplit('.', 1)
        input_format = file_extension
    if input_format not in INPUT_FORMATS:
        print(f"Error: Unsupported input format '{input_format}'")
        return

    inputstr = ""
    if args.input_file == '-':
        inputstr = sys.stdin.read()
    elif not os.path.exists(args.input_file):
        print(f"The file '{args.input_file}' doesn't exist.")
        sys.exit()
    else:
        with open(args.input_file, "r") as f:
            inputstr = f.read()


    if (input_format == 'abif'):
        abifmodel = convert_abif_to_jabmod(inputstr)
    elif (input_format == 'debtally'):
        rawabifstr = convert_debtally_to_abif(inputstr)
        abifmodel = convert_abif_to_jabmod(rawabifstr)
    elif (input_format == 'jabmod'):
        abifmodel = json.loads(inputstr)
    elif (input_format == 'preflib'):
        rawabifstr = convert_preflib_str_to_abif(inputstr)
        abifmodel = convert_abif_to_jabmod(rawabifstr)
    elif (input_format == 'widj'):
        abifmodel = convert_widj_to_jabmod(inputstr)
    else:
        outstr = f"Cannot convert from {input_format} yet."
        print(outstr)
        sys.exit()

    # the "-t/--to" option
    output_format = args.to
    if output_format not in OUTPUT_FORMATS:
        print(f"Error: Unsupported output format '{output_format}'")
        return

    if (output_format == 'abif'):
        outstr = convert_jabmod_to_abif(abifmodel)
    elif (output_format == 'html'):
        outstr = htmltable_pairwise_and_winlosstie(abifmodel)
    elif (output_format == 'html_snippet'):
        outstr = htmltable_pairwise_and_winlosstie(abifmodel,
                                                   snippet = True,
                                                   validate = True,
                                                   modlimit = ABIFMODEL_LIMIT)
    elif (output_format == 'jabmod'):
        outstr = json.dumps(abifmodel, indent=4)
    elif (output_format == 'paircountjson'):
        pairdict = pairwise_count_dict(abifmodel)
        outstr = json.dumps(pairdict, indent=4)
    elif (output_format == 'texttablecountsonly'):
        pairdict = pairwise_count_dict(abifmodel)
        outstr = textgrid_for_2D_dict(
            twodimdict=pairdict,
            tablelabel='   Loser ->\nv Winner')
    elif (output_format == 'texttable'):
        outstr = texttable_pairwise_and_winlosstie(abifmodel)
    elif (output_format == 'winlosstiejson'):
        pairdict = pairwise_count_dict(abifmodel)
        wltdict = winlosstie_dict_from_pairdict(abifmodel['candidates'],
                                                pairdict)
        outstr = json.dumps(wltdict, indent=4)
    else:
        outstr = f"Cannot convert to {output_format} yet."

    print(outstr)


if __name__ == "__main__":
    main()
