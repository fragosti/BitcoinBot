# -*- coding: utf-8 -*-

import time
import json
from sqlite3 import dbapi2 as sqlite3
from hashlib import md5
from datetime import datetime
from flask import Flask, request, session, url_for, redirect, \
     render_template, abort, g, flash, _app_ctx_stack
from werkzeug import check_password_hash, generate_password_hash
import btceapi
from bot.wrappers import simwrapper
from bot.bot import Bot
from bot import defaults
from bot.algorithms import *
import settings


# configuration
DATABASE = 'bitcoinbot.db'
PER_PAGE = 30
DEBUG = True
SECRET_KEY = 'development key'

BOT_DICT = {}
HANDLER = btceapi.KeyHandler(resaveOnDeletion=True)

# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)
app.config.update(dict(
    DATABASE=DATABASE,
    DEBUG=True,
    SECRET_KEY=SECRET_KEY

    ))

def init_bots():
    for bot in get_bots():
        bot_instance = new_bot(bot['algorithm'])
        
        if bot['status'] == 'active':
            bot_instance.start()
        else:
            bot_instance.stop()
        BOT_DICT[str(session['user_id'])+str(bot['bot_name'])] = bot_instance

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    top = _app_ctx_stack.top
    if not hasattr(top, 'sqlite_db'):
        top.sqlite_db = sqlite3.connect(app.config['DATABASE'])
        top.sqlite_db.row_factory = sqlite3.Row
    return top.sqlite_db

def new_bot(algorithm):
    api = simwrapper.BTCESimulationApi(HANDLER)
    algorithm_obj = None
    if algorithm == 'basic':
        algorithm_obj = BasicAlgo(api)
    if algorithm == 'random':
        algorithm_obj = BasicAlgo(api)
    return Bot(algorithm_obj, "ppc_usd")

def get_api_key(id):
    key = query_db('''
        select api_key.* from api_key
        where api_key.who_id = ? ''',
        [session['user_id']])
    if len(key) > 0:
        return key[0]
    else:
        flash("You must submit your API keys")
        return False

def get_bots():
    bots = query_db('''
        select bot.* from bot 
        where owner_id = ?''',
        [session['user_id']])
    return bots

def get_bot_name(id):
    db = get_db()
    name = "DB_ERROR"
    names = query_db('''select bot_name from bot where bot_id = ?''', [id])
    if len(names) > 0:
        name = names[0][0]
    return str(name)

@app.teardown_appcontext
def close_database(exception):
    """Closes the database again at the end of the request."""
    top = _app_ctx_stack.top
    if hasattr(top, 'sqlite_db'):
        top.sqlite_db.close()


def init_db():
    """Creates the database tables."""
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


def query_db(query, args=(), one=False):
    """Queries the database and returns a list of dictionaries."""
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    return (rv[0] if rv else None) if one else rv

@app.route('/api/transaction_history')
def get_transaction_history():
    if request.method == 'GET':
        update_key()
        api = simwrapper.BTCESimulationApi(HANDLER)
        trades = api.getTradeHistory()
        json_list = []
        for trade_obj in trades:
            obj = {}
            obj['pair'] = trade_obj.pair
            obj['type'] = trade_obj.type
            obj['amount'] = float(trade_obj.amount)
            obj['rate'] = float(trade_obj.rate)
            obj['time'] = str(trade_obj.timestamp)
            json_list.append(obj)
        print json_list
        return json.dumps(json_list)


    
    return "hello"




def get_user_id(username):
    """Convenience method to look up the id for a username."""
    rv = query_db('select user_id from user where username = ?',
                  [username], one=True)
    return rv[0] if rv else None


def format_datetime(timestamp):
    """Format a timestamp for display."""
    return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d @ %H:%M')


def gravatar_url(email, size=80):
    """Return the gravatar image for the given email address."""
    return 'http://www.gravatar.com/avatar/%s?d=identicon&s=%d' % \
        (md5(email.strip().lower().encode('utf-8')).hexdigest(), size)


@app.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        g.user = query_db('select * from user where user_id = ?',
                          [session['user_id']], one=True)


@app.route('/')
def dashboard():
    """Shows a users timeline or if no user is logged in it will
    redirect to the public timeline.  This timeline shows the user's
    messages as well as all the messages of followed users.
    """
    if not g.user:
        return redirect(url_for('landing_page'))

    message = query_db('''
        select user.*, api_key.* from user, api_key
        where user.user_id = ? and 
            api_key.who_id = ? ''',
        [session['user_id'], session['user_id']])
    if len(message) > 0:
        message = message[0]

    bots = get_bots()

    return render_template('timeline.html', message=message, bots=bots)


@app.route('/landing')
def landing_page():
    return render_template('landing.html')


@app.route('/public')
def public_timeline():
    """Displays the latest messages of all users."""
    return render_template('timeline.html', messages=query_db('''
        select message.*, user.* from message, user
        where message.author_id = user.user_id
        order by message.pub_date desc limit ?''', [PER_PAGE]))


@app.route('/<username>')
def user_timeline(username):
    """Display's a users tweets."""
    profile_user = query_db('select * from user where username = ?',
                            [username], one=True)
    if profile_user is None:
        abort(404)
    followed = False
    if g.user:
        followed = query_db('''select 1 from follower where
            follower.who_id = ? and follower.whom_id = ?''',
            [session['user_id'], profile_user['user_id']],
            one=True) is not None
    return render_template('timeline.html', messages=query_db('''
            select message.*, user.* from message, user where
            user.user_id = message.author_id and user.user_id = ?
            order by message.pub_date desc limit ?''',
            [profile_user['user_id'], PER_PAGE]), followed=followed,
            profile_user=profile_user)


@app.route('/<username>/follow')
def follow_user(username):
    """Adds the current user as follower of the given user."""
    if not g.user:
        abort(401)
    whom_id = get_user_id(username)
    if whom_id is None:
        abort(404)
    db = get_db()
    db.execute('insert into follower (who_id, whom_id) values (?, ?)',
              [session['user_id'], whom_id])
    db.commit()
    flash('You are now following "%s"' % username)
    return redirect(url_for('user_timeline', username=username))


@app.route('/<username>/unfollow')
def unfollow_user(username):
    """Removes the current user as follower of the given user."""
    if not g.user:
        abort(401)
    whom_id = get_user_id(username)
    if whom_id is None:
        abort(404)
    db = get_db()
    db.execute('delete from follower where who_id=? and whom_id=?',
              [session['user_id'], whom_id])
    db.commit()
    flash('You are no longer following "%s"' % username)
    return redirect(url_for('user_timeline', username=username))

@app.route('/bot', methods=['POST', 'GET'])
def bot():
    if request.method == 'POST' and session['user_id']:
        db = get_db()
        form = request.form
        d = db.execute(''' insert into bot 
            (bot_name, owner_id, trade_amount, floor, ceiling, abs_floor, abs_ceiling, algorithm, status)
            values (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (form['bot_name'], session['user_id'], form['trade_amount'], form['floor'], form['ceiling'], form['abs_floor'], form['abs_ceiling'], form['algorithm'], "inactive"))
        db.commit()
        bot = new_bot(form['algorithm'])

        BOT_DICT[str(session['user_id'])+str(form['bot_name'])] = bot
        flash('Your bot ' + form['bot_name']+' was added!')

        return redirect(url_for('dashboard'))
    if request.method == 'GET':
        return redirect(url_for('dashboard'))

@app.route('/bot/start/<bot_id>')
def start_bot(bot_id):
    if request.method == 'GET':
        db = get_db()
        db.execute('''
            update bot 
            set status = ?
            where bot_id = ? ''',
            ('active', bot_id))
        db.commit()
        name = get_bot_name(bot_id)
        BOT_DICT[str(session['user_id'])+name].start()
        flash('You started your bot ' + name)
        return redirect(url_for('dashboard'))


@app.route('/bot/stop/<bot_id>')
def stop_bot(bot_id):
    if request.method == 'GET':
        db = get_db()
        db.execute('''
            update bot 
            set status = ?
            where bot_id = ? ''',
            ('inactive', bot_id))
        db.commit()
        name = get_bot_name(bot_id)
        BOT_DICT[str(session['user_id'])+name].stop()
        flash('You stopped your bot!')
        redirect(url_for('dashboard'))

@app.route('/bot/delete/<bot_id>')
def delete_bot(bot_id):
    if request.method == 'GET':
        flash("You deleted bot " + get_bot_name(bot_id))
        db = get_db()
        db.execute('''
            delete from bot
            where bot_id = ?
            ''', [bot_id])
        db.commit()
        return redirect(url_for('dashboard'))

@app.route('/add_key', methods=['POST', 'GET'])
def add_key():
    """Add keys for this user"""
    if 'user_id' not in session:
        redirect(url_for('landing_page'))
    if request.form['key'] and request.method == 'POST':
        db = get_db()
        db.execute('''insert into api_key (who_id, key, secret)
            values (?, ?, ?)''', (session['user_id'], 
                                request.form['key'],  
                                request.form['secret']))
        db.commit()
        update_key()
        flash('Your keys were added')
        return redirect(url_for('dashboard'))

def update_key():
    api_key = get_api_key(session['user_id'])
    HANDLER.addKey(str(api_key['key']), str(api_key['secret']), 1)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Logs the user in."""
    if g.user:
        return redirect(url_for('dashboard'))

    error = None
    if request.method == 'POST':
        user = query_db('''select * from user where
            username = ?''', [request.form['username']], one=True)
        if user is None:
            error = 'Invalid username'
        elif not check_password_hash(user['pw_hash'],
                                     request.form['password']):
            error = 'Invalid password'
        else:
            flash('You were logged in')
            session['user_id'] = user['user_id']
            update_key()
            init_bots()
            return redirect(url_for('dashboard'))
    return render_template('login.html', error=error)


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Registers the user."""
    if g.user:
        return redirect(url_for('dashboard'))
    error = None
    if request.method == 'POST':
        if not request.form['username']:
            error = 'You have to enter a username'
        elif not request.form['email'] or \
                 '@' not in request.form['email']:
            error = 'You have to enter a valid email address'
        elif not request.form['password']:
            error = 'You have to enter a password'
        elif request.form['password'] != request.form['password2']:
            error = 'The two passwords do not match'
        elif get_user_id(request.form['username']) is not None:
            error = 'The username is already taken'
        else:
            db = get_db()
            db.execute('''insert into user (
              username, email, pw_hash) values (?, ?, ?)''',
              [request.form['username'], request.form['email'],
               generate_password_hash(request.form['password'])])
            db.commit()
            flash('You were successfully registered and can login now')
            return redirect(url_for('login'))
    return render_template('register.html', error=error)


@app.route('/logout')
def logout():
    """Logs the user out."""
    flash('You were logged out')
    session.pop('user_id', None)
    return redirect(url_for('landing_page'))


# add some filters to jinja
app.jinja_env.filters['datetimeformat'] = format_datetime
app.jinja_env.filters['gravatar'] = gravatar_url


if __name__ == '__main__':
    #init_bots()
    #init_db() 
    #collect_data()
    app.run()
