from __future__ import with_statement
import flask
from flask import Flask
from flask.ext import restful
import shelve
from os import path
from cPickle import HIGHEST_PROTOCOL
from contextlib import closing



SHELVE_DB = 'shelve.db'


app = Flask(__name__)
app.config.from_object(__name__)

db = shelve.open(path.join(app.root_path, app.config['SHELVE_DB']),
                 protocol=HIGHEST_PROTOCOL, writeback=True)


@app.route('/<message>')
def HelloHandler(message):
    db.setdefault('messages', [])
    db['messages'].append(message)
    return app.response_class('\n'.join(db['messages']),
                              mimetype='text/plain')


with closing(db):
    app.run()
    
if __name__ == '__main__':
    api = restful.Api(app)
    api.add_resource(HelloHandler, '/hello')
    app.run(debug=True,  port = 8012, host="0.0.0.0")