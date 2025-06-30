import os
import pandas as pd
from flask import Flask, render_template, request

app = Flask(__name__)

data = [
    {"group": "AKB48", "csv": "member_colors_akb48.csv"},
    {"group": "欅坂46", "csv": "member_colors_keyakizaka46.csv"},
    {"group": "乃木坂46", "csv": "member_colors_nogizaka46.csv"},
]

# CSVディレクトリ
CSV_DIR = os.path.join(os.path.dirname(__file__), '..', 'tables')


def load_all_member_data():
    all_data = []
    for entry in data:
        group = entry["group"]
        filename = entry["csv"]
        filepath = os.path.join(CSV_DIR, filename)

        try:
            df = pd.read_csv(filepath)
            df["グループ"] = group  # グループ列を明示的に追加
            df = df.rename(columns={
                "名前": "name",
                "カラー": "color",
                "顔": "face",
                "グループ": "group"
            })

            if "face" not in df.columns:
                df["face"] = ""

            all_data.append(df)
        except Exception as e:
            all_data.append(pd.DataFrame([{"name": "読み込み失敗", "color": str(e), "face": "", "group": group}]))

    return pd.concat(all_data, ignore_index=True)


# アプリのルート
@app.route("/", methods=["GET", "POST"])

def index():
    df = load_all_member_data()
    group_list = sorted({entry["group"] for entry in data})
    results = []

    if request.method == "POST":
        group_query = request.form["group"]
        name_query = request.form["name"]
        results_df = df[
            df["group"].str.contains(group_query, na=False) &
            df["name"].str.contains(name_query, na=False)
        ]
        results = results_df.to_dict(orient="records")

    return render_template("index.html", results=results, groups=group_list)

if __name__ == "__main__":
    app.run(debug=True)
