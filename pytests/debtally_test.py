from abiftestfuncs import *
import json
import subprocess
import os
import re
import glob
import sys
import pytest

testdicts=[
    {
        "fetchspec":"debian-elections.fetchspec.json",
        'outformat':"jabmod",
        'filename':"downloads/debian-elections/2022/vote_002_tally.txt",
        'key1':"metadata",
        'subkey1':"ballotcount",
        'val1':354
    },
    {
        "fetchspec":"debian-elections.fetchspec.json",
        'outformat':"paircountjson",
        'filename':"downloads/debian-elections/2003/leader2003_tally.txt",
        'key1':"MichlmayrMartinAAJ7",
        'subkey1':"GarbeeBdaleMEIQ",
        'val1':228
    },
    {
        "fetchspec":"debian-elections.fetchspec.json",
        'outformat':"paircountjson",
        'filename':"downloads/debian-elections/2003/leader2003_tally.txt",
        'key1':"GarbeeBdaleMEIQ",
        'subkey1':"MichlmayrMartinAAJ7",
        'val1':224
    },
    {
        "fetchspec":"debian-elections.fetchspec.json",
        'outformat':"jabmod",
        'filename':"downloads/debian-elections/2021/vote_002_tally.txt",
        'key1':"metadata",
        'subkey1':"ballotcount",
        'val1':420
    }
]

mycols = ('outformat', 'filename', 'key1', 'subkey1', 'val1')

pytestlist = []
for testdict in testdicts:
    myparam = get_pytest_abif_testsubkey(testdict, cols=mycols)
    pytestlist.append(myparam)


print(f"{pytestlist=}")

@pytest.mark.parametrize(mycols, pytestlist)
def test_filename(outformat, filename, key1, subkey1, val1):
    """Testing debtally"""
    try:
        fh = open(filename, 'rb')
    except:
        print(f'Missing file: {filename}')
        print(
            "Please run './fetchmgr.py *.fetchspec.json' " +
            "if you haven't already")
        sys.exit()

    cmd_args = ["-f", "debtally", "-t", outformat, filename]
    abiftool_output = get_abiftool_output_as_array(cmd_args)
    outputdict = json.loads("\n".join(abiftool_output))

    import abiflib
    devobj = abiflib.LogfileSingleton()
    devobj.log(json.dumps(outputdict, indent=4))

    assert outputdict[key1][subkey1] == val1
