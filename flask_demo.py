from flask import Flask
from flask import render_template


app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')


def _main():
    app.run(debug=True)


if __name__ == '__main__':
    _main()
