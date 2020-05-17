#! /usr/bin/env python
"""
This program reads commiters from a csv file and reads them into the database.
"""

import argparse
import csv
import psycopg2
from git_log import Committer


def arguments():
    """Parse the commandline arguments and return a argparse object."""
    parser = argparse.ArgumentParser(description='Read commiters from csv')
    parser.add_argument('--path', help='The path to csv', required=True)
    return parser.parse_args()


def main():
    """This is the main program to read the csv files"""
    args = arguments()
    con = psycopg2.connect("")
    con.autocommit = True
    # Lets create a cursor to query postgres
    cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)

    print('Reading committers from', args.path)
    with open(args.path) as csvfile:
        spamreader = csv.reader(csvfile)
        for row in spamreader:
            company, name, mail = row[0:3]
            Committer(name, mail, company).get_id(cur)
