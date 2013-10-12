#coding: utf-8

from flask.ext.script import Manager

from pallas import app as server_app


app = server_app.build()
manager = Manager(app)


@manager.command
def run():
    app.run(host='0.0.0.0', port=9002, debug=True)


if __name__ == '__main__':
    manager.run()
