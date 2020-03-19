import json
import os

from flask import Flask

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/healthCheck')
def health_check():
    return (
        json.dumps({'success': True}),
        200,
        {'ContentType': 'application/json'},
    )


if __name__ == '__main__':
    app.run(
        host=os.getenv("APP_HOST"),
        port=int(os.getenv("APP_HOST"))
    )
