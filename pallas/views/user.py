#coding: utf-8

from datetime import datetime
from time import time

from flask import (Blueprint, current_app, render_template, session, request,
                   redirect, abort, jsonify, url_for, g)
from flask.ext.rq import get_queue, get_connection
from rq.job import Job

from pallas.forms.user import LoginForm
from pallas.utils import LoginRequired, check_login
from pallas.tasks import sync_user

app = Blueprint('user', __name__, template_folder='../templates')


@app.before_request
def init_app():
    # 获取登录用户信息
    cardno = session.get('cardno', None)
    if cardno and check_login():
        g.user = current_app.mongo.db.users.find_one({'cardno': cardno})


@app.route('/login', methods=['GET', 'POST'])
def login():
    form, next = LoginForm(), request.args.get('next', '/')
    cookies = form.validate_login()
    if cookies:
        session['cardno'] = form.cardno.data
        session['token'] = cookies.values()[0]
        return redirect(request.args.get('next', '/'))
    return render_template('user/login.html', form=form, next=next)


@app.route('/logout', methods=['GET'])
@LoginRequired()
def logout():
    session.pop('token')
    return redirect('/')


@app.route('/sync', methods=['GET', 'POST'])
@LoginRequired('/user/sync')
def sync():
    # 检查是否可以进行同步
    if (time() - g.user['last_updated'] <
       current_app.config['TASKS']['user']['update_interval']):
        abort(403)

    form = LoginForm()

    if form.validate_login():
        cardno, password = form.cardno.data, form.password.data
        job = get_queue('user').enqueue(sync_user, cardno, password)
        session['sync_job'] = job.id
        return redirect(url_for('.sync_progress'))

    return render_template('user/sync.html', form=form)


def get_current_job():
    job_id = session.get('sync_job', None)
    if job_id:
        return Job.fetch(job_id, connection=get_connection())


def get_current_job_or_404():
    return get_current_job() or abort(404)


@app.route('/sync/progress', methods=['GET'])
@LoginRequired('/user/sync/progress')
def sync_progress():
    job = get_current_job_or_404()
    return jsonify(progress=job.meta.get('progress', 0.0))


@app.route('/sync/next', methods=['GET'])
@LoginRequired('/user/sync/next')
def sync_next():
    # 根据上次同步计算下次更新时间
    interval = current_app.config['TASKS']['user']['update_interval']
    next = g.user.get('last_updated', time() - interval) + interval

    # 如果当前在进行更新，则修改时间为当前时间 + interval 之后
    job = get_current_job()
    if job.meta.get('progress', 0) < 1:
        next = time() + interval

    return jsonify(next=max(datetime.fromtimestamp(next), datetime.utcnow()))
