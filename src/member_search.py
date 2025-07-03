import os
import pandas as pd
from flask import Flask, render_template, request, send_from_directory
from idol_name_detector import analyze_image_with_gemini
from dotenv import load_dotenv
from Flyer_Info_Get import get_flyer_info_with_gemini

load_dotenv()
app = Flask(__name__)

# CSVディレクトリ
CSV_DIR = os.path.join(os.path.dirname(__file__), '..', 'tables')

# imagesディレクトリ
IMG_DIR = os.path.join(os.path.dirname(__file__), '..', 'images')

@app.route('/images/faces/<filename>')
def serve_image(filename):
    return send_from_directory(os.path.join(app.root_path, "..", "images", "faces"), filename)

def load_index_data():
    try:
        df = pd.read_csv(os.path.join(CSV_DIR, "index.csv"))
        df = df.rename(columns={"グループ名": "group", "ファイル名": "csv"})
        return df.to_dict(orient="records")
    except Exception as e:
        print(f"[ERROR] index.csv の読み込み失敗: {e}")
        return []

def load_all_member_data():
    all_data = []
    index_data = load_index_data()
    for entry in index_data:
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

            for _, row in df.iterrows():
                name = row["name"]
                face_image_path = os.path.join(IMG_DIR, "faces", f"{name}.jpg")
                if os.path.exists(face_image_path):
                    df.loc[row.name, "face"] = f"/images/faces/{row['name']}.jpg"
                else:
                    df.loc[row.name, "face"] = ""

            all_data.append(df)
        except Exception as e:
            print(e)
            all_data.append(pd.DataFrame([{"name": "読み込み失敗", "color": str(e), "face": "", "group": group}]))

    return pd.concat(all_data, ignore_index=True)


# アプリのルート
@app.route("/", methods=["GET", "POST"])

def index():
    index_data = load_index_data()
    group_list = sorted({entry["group"] for entry in index_data})
    results = []
    gemini_result = ""
    gemini_result_flyer = ""
    search_mode = "name"

    if request.method == "POST":
        group_query = request.form.get("group","")
        name_query = request.form.get("name","")
        image_file = request.files.get("image")
        flyer_file = request.files.get("flyer")

        if image_file and image_file.filename != "":
            search_mode = "image"
            # 画像検索処理

            upload_folder = os.path.join(os.path.dirname(__file__), 'uploaded_images')
            os.makedirs(upload_folder, exist_ok=True)
            image_path = os.path.join(upload_folder, image_file.filename)
            image_file.save(image_path)

            # Geminiモデルを使って画像解析
            gemini_result = analyze_image_with_gemini(image_path, group_query)

        elif flyer_file and flyer_file.filename != "":
            search_mode = "flyer"
            # フライヤー検索処理

            upload_folder = os.path.join(os.path.dirname(__file__), '..', 'images', 'flyers')
            os.makedirs(upload_folder, exist_ok=True)
            flyer_path = os.path.join(upload_folder, flyer_file.filename)
            flyer_file.save(flyer_path)

            # Geminiモデルを使って画像解析
            gemini_result_flyer = get_flyer_info_with_gemini(flyer_path)

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

    return render_template("index.html", results=results, groups=group_list, gemini_output=gemini_result, mode=search_mode, gemini_output_flyer=gemini_result_flyer)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)
