#! /usr/bin/env python3

import sys
import urllib.request
import pds3parse
import json

def main(argv=None):
    '''
    Extract command line arguments, ensure that the script is not already running,
    and process the current upload directory.
    '''
    if argv is None:
        argv = sys.argv

    url = argv[1]

    with urllib.request.urlopen(url) as f:
        data = f.read().decode('utf-8')
        keywords = pds3parse.do_parse(data)
        print(json.dumps(keywords))


if __name__ == '__main__':
  sys.exit(main())
