#coding: utf-8

from flask import Blueprint
from flask import render_template, session, request, redirect

from pallas.forms.user import LoginForm
from pallas.utils import LoginRequired

app = Blueprint('user', __name__)


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
