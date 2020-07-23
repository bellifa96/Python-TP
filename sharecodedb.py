#!/usr/bin/env python3
import sqlite3

from flask import Flask, request, render_template, \
    redirect

from model_sqlite import save_doc_as_file_sqlite, \
    read_doc_as_file_sqlite, \
    get_last_entries_from_files_sqlite

app = Flask(__name__)

connection = sqlite3.connect('tp.db')
cursor = connection.cursor()

cursor.execute('CREATE TABLE IF NOT EXISTS SHARECODE(ID INTEGER PRIMARY KEY AUTOINCREMENT,Uid CHAR(50), '
               'Code text, Langage CHAR(50))')
cursor.execute('CREATE TABLE IF NOT EXISTS INFOUSER(ID INTEGER PRIMARY KEY AUTOINCREMENT, Uid CHAR(50), IP CHAR(50),'
               'HOSTNAME CHAR(50),NAVIGATOR CHAR(50), CREATED_AT CHAR(50), LAST_MODIFICATION CHAR(50))')


connection.commit()
connection.close()

@app.route('/')
def index():
    # d = { 'last_added':[ { 'uid':'testuid', 'code':'testcode' } ] }
    d = {'last_added': get_last_entries_from_files_sqlite()}
    return render_template('index.html', **d)


@app.route('/create')
def create():
    uid = save_doc_as_file_sqlite()
    return redirect("{}edit/{}".format(request.host_url, uid))


@app.route('/edit/<string:uid>/')
def edit(uid):
    code = read_doc_as_file_sqlite(uid)
    if code is None:
        return render_template('error.html', uid=uid)
    d = dict(uid=uid, code=code,
             url="{}view/{}".format(request.host_url, uid))
    return render_template('edit.html', **d)


@app.route('/publish', methods=['POST'])
def publish():
    code = request.form['code']
    uid = request.form['uid']
    langage = request.form['langage']
    save_doc_as_file_sqlite(uid, code, langage)
    return redirect("{}{}/{}".format(request.host_url,
                                     request.form['submit'],
                                     uid))


@app.route('/view/<string:uid>/')
def view(uid):
    code = read_doc_as_file_sqlite(uid)
    if code is None:
        return render_template('error.html', uid=uid)
    d = dict(uid=uid, code=code,
             url="{}view/{}".format(request.host_url, uid))
    return render_template('view.html', **d)


@app.route('/admin/')
def admin():
    pass


if __name__ == '__main__':
    app.run()
