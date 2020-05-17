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

import datetime
import re
import psycopg2
import psycopg2.extras

__version__ = "0.1"

COMMITTERS = {}
COMMITTERS_PER_COMPANY = {}
DTFORMAT = '%a %b %d %H:%M:%S %Y %z'
RE_CHANGES = re.compile(r" *(?P<files>[0-9]+) files? changed,?"
                        r"( *(?P<inserts>[0-9]+) insertions?\(\+\))?,?"
                        r"( *(?P<deletes>[0-9]+) deletions?\(\-\))?")


def __run_sql(cur, query, values=()):
    """Run a query and get the results"""
    # print(query, values)
    cur.execute(query, values)
    try:
        return cur.fetchall()
    except psycopg2.ProgrammingError:
        return None


def __run_sql_get_one_field(cur, query, values=(), default=None):
    """Run a query and get first col of first row"""
    try:
        result = __run_sql(cur, query, values)
        return result[0][0]
    except IndexError:
        return default


class Repository(list):
    """This class represents a repository"""
    path = None
    __id = None

    def __init__(self, path):
        super(Repository, self).__init__()
        self.path = path

    def get_id(self, cur):
        """This method can be used to get the id from the database.

        If needed it will write this object to the database."""
        if self.__id:
            return self.__id

        # No __id yet. Lets see if it is inserted. Find by mail.
        query = "select id from repository where path = %s"
        self.__id = __run_sql_get_one_field(cur, query, (self.path,))

        if self.__id:
            return self.__id

        # raise Exception('Unknown repository. Please add manually.')
        query = 'insert into repository (path) values(%s) RETURNING id'
        self.__id = __run_sql_get_one_field(cur, query, (self.path,))
        if not self.__id:
            raise Exception('Coud not add unknown repository.', self.path)
        return self.__id

    def __repr__(self):
        return "Repository({})".format({'path': self.path, '__id': self.__id})


class Committer(list):
    """This class represents a commiter on a repo"""
    name = None
    mail = None
    company = 'Other'
    __id = None

    def __init__(self, name, mail=None, company=None):
        if not name:
            raise Exception('Cannot create a committer without a name')
        super(Committer, self).__init__()
        if not mail and '<' in name:
            parts = name.split(" <", 2)
            name = parts[0]
            mail = parts[1]
            if mail[-1] == '>':
                mail = mail[:-1]
        self.name = name
        self.mail = mail
        added = False
        if mail not in COMMITTERS:
            COMMITTERS[mail] = self
            added = True
        if name not in COMMITTERS:
            COMMITTERS[name] = self
            added = True
        if added:
            self.set_company(company)

    def set_company(self, company):
        """This method can be used to set the correct company"""
        if not company and not self.company:
            return
        if self.company == company:
            return
        if self.company:
            try:
                COMMITTERS_PER_COMPANY[self.company].remove(self)
            except KeyError:
                pass
        if company:
            try:
                COMMITTERS_PER_COMPANY[self.company].append(self)
            except KeyError:
                COMMITTERS_PER_COMPANY[self.company] = [self]

    def get_id(self, cur):
        """This method can be used to write this obejt to the database"""
        if self.__id:
            return self.__id

        # No __id yet. Lets see if it is inserted. Find by mail.
        if self.mail:
            query = "select id from committer where email = %s"
            self.__id = __run_sql_get_one_field(cur, query, (self.mail,))

        if self.__id:
            return self.__id

        # No __id yet. Lets see if it is inserted. Find by name.
        if not self.__id and self.name:
            # First by name
            query = "select id from committer where name = %s"
            self.__id = __run_sql_get_one_field(cur, query, (self.name,))

        if self.__id:
            return self.__id
        # First retrieve and/or create company
        query = "select id from company where name = %s"
        company_id = __run_sql_get_one_field(cur, query, (self.company,))
        if not company_id:
            query = 'insert into company (name) values(%s) RETURNING id'
            company_id = __run_sql_get_one_field(cur, query, (self.company,))
        query = str('insert into committer (name, email, companyid) '
                    'values(%s, %s, %s) RETURNING id')
        self.__id = __run_sql_get_one_field(cur, query, (self.name, self.mail,
                                                         company_id))
        return self.__id

    def __repr__(self):
        return "Committer({})".format({'name': self.name, 'mail': self.mail,
                                       'company': self.company,
                                       '__id': self.__id})


class Commit():
    """This class reresents a commit object.

    Every commit object has an author, a date, a hash and a Reviewer"""
    repo = None
    hash = None
    author = None
    reviewer = None
    date = None
    changes = None
    __body = None

    def __init__(self, repo, body):
        """This method initializes this commit from a commit body"""
        self.__body = body
        self.repo = repo
        self.changes = None, None, None
        if isinstance(body, str):
            body = body.split("\n")
        for line in body:
            if line.startswith("commit "):
                parts = line.split(" ")
                self.hash = parts[1]
                continue
            if line.startswith("Date: "):
                line = line[5:].lstrip()
                self.date = datetime.datetime.strptime(line, DTFORMAT)
                continue
            line = line.strip()
            if line.startswith("Author: "):
                if self.author and not self.reviewer:
                    self.reviewer = self.author
                line = line[8:]
                author = Committer(line)
                # Might be that author alreadye xistsed. Than the object
                # creates, but does not overwrite COMMITTERS.
                # Lets get the one from COMMITTERS.
                try:
                    author = COMMITTERS[author.mail]
                except KeyError:
                    author = COMMITTERS[author.name]
                self.author = author
                author.append(self)

            else:
                match = RE_CHANGES.search(line)
                if match:
                    self.changes = (match.group('files'),
                                    match.group('inserts'),
                                    match.group('deletes'))

    def write_to_db(self, cur):
        """This method can be used to write this object to the database"""
        repoid = self.repo.get_id(cur)
        authorid = reviewerid = None
        if self.author:
            authorid = self.author.get_id(cur)
        if self.reviewer:
            reviewerid = self.reviewer.get_id(cur)
        query = str("select count(*) from commit "
                    "where repoid = %s and hash = %s")
        exists = __run_sql_get_one_field(cur, query, (repoid, self.hash))
        if exists > 0:
            query = str("update commit set authorid = %s, reviewerid = %s, "
                        "dt = %s, files = %s, inserts = %s, "
                        "deletes = %s where repoid = %s and hash = %s")
            fields = (authorid, reviewerid, self.date)
            fields += self.changes
            fields += (repoid, self.hash)
            __run_sql(cur, query, fields)
            return
        query = str("insert into commit "
                    "values (%s, %s, %s, %s, %s, %s, %s, %s)")
        fields = (repoid, self.hash, authorid, reviewerid, self.date)
        fields += self.changes
        __run_sql(cur, query, fields)

    def __repr__(self):
        """String representation of the object"""
        ret = {}
        ret['repo'] = self.repo
        ret['hash'] = self.hash
        ret['author'] = self.author
        ret['reviewer'] = self.reviewer
        ret['reviewer'] = self.reviewer
        ret['changes'] = self.changes
        ret['__body'] = self.__body
        return "Commit({})".format(str(ret))
