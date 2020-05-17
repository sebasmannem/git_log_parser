#! /usr/bin/env python
"""
This program finds authors and reviewers for git logs.

The result is pushed into a database to be parsed into numbers.

Example commit:

commit af3290f5e790dcd1be3ac209be1805626f4ebac8 (HEAD -> master, origin/master)
Author: Amit Kapila <akapila@postgresql.org>
Date:   Thu Dec 12 11:51:30 2019 +0530

    Change overly strict Assert in TransactionGroupUpdateXidStatus.

    This Assert thought that an overflowed transaction can never get registered
    for the group update.  But that is not true, because even when the number
    of children for a transaction got reduced, the overflow flag is not
    changed.  And, for group update, we only care about the current number of
    children for a transaction that is being committed.

    Based on comments by Andres Freund, remove a redundant Assert in
    TransactionIdSetPageStatus as we already had a static Assert for the same
    condition a few lines earlier.

    Reported-by: Vignesh C
    Author: Dilip Kumar
    Reviewed-by: Amit Kapila
    Backpatch-through: 11
    Discussion: https://postgr.es/m/CAFiTN-s5=uJw-Z6JC9gcqtB...@mail.gmail.com

 src/backend/access/transam/clog.c | 13 +++----------
 1 file changed, 3 insertions(+), 10 deletions(-)

"""

import argparse
import sys
import psycopg2
import psycopg2.extras
from git_log import Repository, Commit


def arguments():
    """Parse the commandline arguments and return a argparse object."""
    parser = argparse.ArgumentParser(description='Download content')
    parser.add_argument('--path', help='The path to parse', required=True)
    return parser.parse_args()


def main():
    """This is the main program to run"""
    args = arguments()
    repo = Repository(args.path)
    con = psycopg2.connect("")
    con.autocommit = True
    # Lets create a cursor to query postgres
    cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)

    commits = []

    commit_lines = []
    for line in sys.stdin:
        line = line.rstrip()
        if line.startswith("commit ") and commit_lines:
            commit = Commit(repo, commit_lines)
            try:
                commit.write_to_db(cur)
            except Exception:
                print(commit)
                raise
            commits.append(commit)
            commit_lines = [line]
            if len(commits) % 100 == 0:
                print("Parsed {} commits".format(len(commits)))
        else:
            commit_lines.append(line)
    if len(commits) % 1000 != 0:
        print("Parsed {} commits".format(len(commits)))


main()
