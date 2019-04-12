#! /usr/bin/env python3
'''
Python script to process submissions from Catalina Sky Survey and convert them
to PDS4 format.
'''

import sys

import os
import os.path
import itertools
import subprocess
from product import Product
from collection import Collection
from bundle import Bundle
from bs4 import BeautifulSoup
import json

def main(argv=None):
    '''
    Extract command line arguments, ensure that the script is not already running,
    and process the current upload directory.
    '''
    if argv is None:
        argv = sys.argv

    basedir = argv[1]

    print(process_upload_dir(basedir))

    return 0

def process_upload_dir(basedir):
    '''
    process an upload directory, assuming it has been validated.
    '''
    bundles = discover_bundles(basedir)
    products = discover_products(basedir)
    collections = discover_collections(basedir)

    result = {
        "bundles": [x.keywords for x in bundles],
        "products": [x.keywords for x in products],
        "collections": [x.keywords for x in collections]
    }

    return json.dumps(result, indent=2)

def discover_bundles(basedir):
    '''
    Find all of the product labels in the directory and convert them
    to product objects
    '''
    files = [x for x in get_label_files(basedir) if is_bundle(x)]
    bundles = [Bundle(basedir, infile) for infile in files]
    return bundles


def discover_products(basedir):
    '''
    Find all of the product labels in the directory and convert them
    to product objects
    '''
    files = [x for x in get_label_files(basedir) if is_product(x)]
    products = [Product(basedir, infile) for infile in files]
    return products

def discover_collections(basedir):
    '''
    Find all of the product labels in the directory and convert them
    to product objects
    '''
    files = [x for x in get_label_files(basedir) if is_collection(x)]
    collections = [Collection(basedir, infile) for infile in files]
    return collections

def is_label(candidate):
    '''
    Determines if the given file is a label file.
    '''
    return candidate.endswith('.xml')

def is_product(file):
    with open(file) as f:
        s = BeautifulSoup(f, 'lxml-xml')
        return s.Product_Observational

def is_collection(file):
    with open(file) as f:
        s = BeautifulSoup(f, 'lxml-xml')
        return s.Product_Collection

def is_bundle(file):
    with open(file) as f:
        s = BeautifulSoup(f, 'lxml-xml')
        return s.Product_Bundle

def get_label_files(dirname):
    return (x for x in find_files(dirname) if is_label(x))

def find_files(dirname):
    '''
    Gets all of the files in a directory.
    '''
    filelists = [[os.path.join(subdir, f) for f in files] for subdir, _, files in os.walk(dirname)]
    return itertools.chain.from_iterable(filelists)


def read_file(filename):
    '''
    One-liner to read a file
    '''
    with open(filename) as infile:
        return infile.read()

def write_file(filename, contents):
    '''
    One-liner to write a file
    '''
    path = os.path.dirname(filename)
    os.makedirs(path, exist_ok=True)
    with open(filename, "w") as outfile:
        outfile.write(contents)

if __name__ == '__main__':
    sys.exit(main())
