#coding: utf-8

from flask import (Blueprint, current_app, render_template, session, request,
                   redirect, abort, jsonify, url_for, g)
from flask.ext.rq import get_queue

from pallas.forms.user import LoginForm
from pallas.tasks import sync_user
from pallas.helpers.user import LoginRequired, check_login, api_login_required
from pallas.helpers.job import (get_current_job_or_404, get_next_job_time,
                                is_job_performable)

app = Blueprint('user', __name__, template_folder='../templates')


@app.before_request
def init_app():
    # 获取当前登录用户信息
    cardno = session.get('cardno', None)
    if cardno and check_login():
        g.user = current_app.mongo.db.users.find_one({'cardno': cardno})
    else:
        g.user = None


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
    if not is_job_performable():
        abort(403)

    form = LoginForm()
    if form.validate_login():
        cardno, password = form.cardno.data, form.password.data
        job = get_queue('user').enqueue(sync_user, cardno, password)
        session['sync_job'] = job.id
        return redirect(url_for('.sync_progress'))
    return render_template('user/sync.html', form=form)


@app.route('/sync/progress', methods=['GET'])
@api_login_required
def sync_progress():
    job = get_current_job_or_404()
    return jsonify(progress=job.meta.get('progress', 0.0))


@app.route('/sync/next', methods=['GET'])
@api_login_required
def sync_next():
    '''获取可以进行下一个任务的时间

    如果当前时间（timestamp）大于返回值，就可以进行
    '''
    return jsonify(next=get_next_job_time())
