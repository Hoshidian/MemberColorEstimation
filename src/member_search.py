import os
import pandas as pd
from flask import Flask, render_template, request
from idol_name_detector import analyze_image_with_gemini
from dotenv import load_dotenv

load_dotenv()
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
    group_list = sorted({entry["group"] for entry in data})
    results = []
    gemini_result = ""
    search_mode = "name"

    if request.method == "POST":
        group_query = request.form.get("group","")
        name_query = request.form.get("name","")
        image_file = request.files.get("image")

        if image_file and image_file.filename != "":
            search_mode = "image"
            # 画像検索処理

            upload_folder = os.path.join(os.path.dirname(__file__), 'uploaded_images')
            os.makedirs(upload_folder, exist_ok=True)
            image_path = os.path.join(upload_folder, image_file.filename)
            image_file.save(image_path)

            # Geminiモデルを使って画像解析
            gemini_result = analyze_image_with_gemini(image_path, group_query)

        elif group_query.strip() != "" or name_query.strip() != "":
            search_mode = "name"
            # 名前検索処理

            df = load_all_member_data()

            results_df = df[
                df["group"].str.contains(group_query, na=False) &
                df["name"].str.contains(name_query, na=False)
            ]
            results = results_df.to_dict(orient="records")

        else:
            search_mode = "name"
            results = load_all_member_data().to_dict(orient="records")

    return render_template("index.html", results=results, groups=group_list, gemini_output=gemini_result, mode=search_mode)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)
