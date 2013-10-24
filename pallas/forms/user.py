#coding: utf-8

from flask_wtf import Form
from wtforms.fields import TextField, PasswordField
from wtforms.validators import DataRequired, Length

import api
from api import LibraryLoginError, LibraryChangePasswordError


__all__ = ['LoginForm']


class LoginForm(Form):
    '''用户登录表单'''

    cardno = TextField('cardno', validators=[DataRequired(),
                                             Length(min=10, max=10)])
    password = PasswordField('password', validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        # 表单错误提示
        self.error = ''

    def validate_login(self):
        '''用户登录验证'''

        if not self.validate_on_submit():
            return

        cardno, password = self.cardno.data, self.password.data
        user = api.Me()
        try:
            return user.login(cardno, password)
        except LibraryChangePasswordError, e:
            self.error = u'需要到 %s 激活帐号' % e.next
        except LibraryLoginError, e:
            self.error = u'用户名或密码错误'
        except Exception:
            self.error = u'网络错误'
