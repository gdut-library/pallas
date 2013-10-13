#coding: utf-8

from flask import Blueprint
from flask import render_template, session, request, redirect
from flask.ext.rq import get_queue

from pallas.forms.user import LoginForm
from pallas.utils import LoginRequired
from pallas.tasks import sync_user

app = Blueprint('user', __name__, template_folder='../templates')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    cookies = form.validate_login()
    if cookies:
        session['cardno'] = form.cardno.data
        session['token'] = cookies.values()[0]
        return redirect(request.args.get('next', '/'))
    return render_template('user/login.html', form=form)


@app.route('/logout', methods=['GET'])
@LoginRequired()
def logout():
    session.pop('token')
    return redirect('/')


@app.route('/sync', methods=['GET', 'POST'])
@LoginRequired('/user/sync')
def sync():
    form = LoginForm()
    if form.validate_login():
        job = get_queue('user').enqueue(sync_user, form.cardno.data,
                                        form.password.data)
        return job.id
    return render_template('user/sync.html', form=form)
