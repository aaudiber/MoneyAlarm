from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World!"

@app.route("/wakeuptime", methods=['POST'])
def update_wakeuptime():
    lateness = request.lateness
    name = request.username


if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=8080)
