#!/usr/bin/env python3

import os
import sqlite3
import socket
from datetime import datetime
from itertools import chain
from random import choice
from string import ascii_letters, digits
from flask import request


def create_uid_sqlite(n=9):
    '''Génère une chaîne de caractères alétoires de longueur n
   en évitant 0, O, I, l pour être sympa.'''
    chrs = [c for c in chain(ascii_letters, digits)
            if c not in '0OIl']
    return ''.join((choice(chrs) for i in range(n)))


def save_doc_as_file_sqlite(uid=None, code=None, langage=None, null=None):
    '''Crée/Enregistre le document sous la forme d'un fichier
    data/uid. Return the file name.
    '''
    hostname = socket.gethostname()
    IPAddr = socket.gethostbyname(hostname)
    navigator = request.user_agent.browser
    now = datetime.now()  # current date and time
    date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
    if uid is None:
        uid = create_uid_sqlite()
        code = '# Write your code here...'
        langage = ''

        connection = sqlite3.connect('tp.db')
        cursor1 = connection.cursor()
        cursor1.execute("INSERT INTO SHARECODE VALUES(?, ?, ?, ?)", (null, uid, code, langage))
        cursor1.execute("INSERT INTO INFOUSER VALUES(?, ?, ?, ?, ?, ?, ?)",
                        (null, uid, IPAddr, hostname, navigator, date_time, date_time))
        connection.commit()
        connection.close()
    connection = sqlite3.connect('tp.db')
    cursor1 = connection.cursor()
    cursor1.execute('''UPDATE SHARECODE SET Code = ?, Langage = ? WHERE Uid = ? ''', (code, langage, uid))
    cursor1.execute('''UPDATE INFOUSER SET LAST_MODIFICATION = ?, IP = ?,HOSTNAME = ?,NAVIGATOR = ?  WHERE Uid = ? ''',
                    (date_time, IPAddr, hostname, navigator, uid))
    connection.commit()
    connection.close()
    with open('data/{}'.format(uid), 'w') as fd:
        fd.write(code)
    with open('data/{}'.format(uid + '.lang'), 'w') as fd:
        fd.write(langage)
    return uid


def read_doc_as_file_sqlite(uid):
    '''Lit le document data/uid'''
    try:
        with open('data/{}'.format(uid)) as fd:
            code = fd.read()
        return code
    except FileNotFoundError:
        return None


def get_last_entries_from_files_sqlite(n=10, nlines=10):
    entries = os.scandir('data')
    d = []
    entries = sorted(list(entries),
                     key=(lambda e: e.stat().st_mtime),
                     reverse=True)
    for i, e in enumerate(entries):
        if i >= n:
            break
        if e.name.startswith('.'):
            continue
        with open('data/{}'.format(e.name)) as fd:
            code = ''.join((fd.readline() for i in range(nlines)))
            if fd.readline():
                code += '\n...'
        connection = sqlite3.connect('tp.db')
        cursor1 = connection.cursor()
        connection.commit()
        connection.close()
        d.append({'uid': e.name, 'code': code})
    return d


def get_last_entries_from_files_admin_sqlite(n=10, nlines=10):
    entries = os.scandir('data')
    d = []
    user = ""
    entries = sorted(list(entries),
                     key=(lambda e: e.stat().st_mtime),
                     reverse=True)
    for i, e in enumerate(entries):
        if i >= n:
            break
        if '.lang' in e.name:
            continue
        with open('data/{}'.format(e.name)) as fd:
            code = ''.join((fd.readline() for i in range(nlines)))
            if fd.readline():
                code += '\n...'
        uid = str(e.name)
        print(uid)
        connection = sqlite3.connect('tp.db')
        cursor1 = connection.cursor()
        ip = cursor1.execute('''SELECT IP FROM INFOUSER where Uid = ? ''', (uid,));
        ip = ip.fetchone()
        host = cursor1.execute('''SELECT HOSTNAME FROM INFOUSER where Uid = ? ''', (uid,));
        host = host.fetchone()
        navigator = cursor1.execute('''SELECT navigator FROM INFOUSER where Uid = ? ''', (uid,));
        navigator = navigator.fetchone()
        create_date = cursor1.execute('''SELECT created_at FROM INFOUSER where Uid = ? ''', (uid,));
        create_date = create_date.fetchone()
        modified_date = cursor1.execute('''SELECT last_modification FROM INFOUSER where Uid = ? ''', (uid,));
        modified_date = modified_date.fetchone()
        print(user)
        connection.commit()
        connection.close()
        d.append({'uid': e.name, 'code': code, 'ip': ip, 'navigator': navigator, 'host': host, 'create_date': create_date, 'modified_date': modified_date})
    print(user)
    return d
