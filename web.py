from flask import Flask, request

app = Flask(__name__)


@app.route('/<name>')
def hello(name):
    return f"Hello <b>{name}</b>"


if __name__ == '__main__':
    app.run('0.0.0.0', port=4443, ssl_context=('server.pem','server.key'))
