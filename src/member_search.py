from flask import Flask, render_template, request

app = Flask(__name__)

data = [
    {"group": "aaa", "name": "abc1", "face": "face1", "color": "赤"},
    {"group": "bbb", "name": "xyz2", "face": "face2", "color": "青"},
]

@app.route("/", methods=["GET", "POST"])
def index():
    results = []
    if request.method == "POST":
        group = request.form["group"]
        name = request.form["name"]
        results = [d for d in data if group in d["group"] and name in d["name"]]
    return render_template("index.html", results=results)

if __name__ == "__main__":
    app.run(debug=True)
