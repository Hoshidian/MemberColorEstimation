import base64
import requests
import os
import csv
import re
import google.generativeai as genai
from PIL import Image

def get_flyer_info_with_gemini(image_path: str):
    """
    指定された画像をGeminiモデルで分析し、CSVファイルを作成します。

    Args:
        image_path (str): 分析する画像のパス。

    Returns:
        str: 画像から抽出したグループ名とメンバー、メンバーカラー情報。
    """

    # 画像ファイルを読み込む
    img = Image.open(image_path)

    print ("image path:", image_path)
    # Base64エンコード
    with open(image_path, "rb") as f:
        image_bytes = f.read()
        image_base64 = base64.b64encode(image_bytes).decode("utf-8")


    # APIキーとエンドポイント
    API_KEY=os.getenv("GEMINI_API_KEY")
    genai.configure(api_key=API_KEY)
    API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"

    # モデルの選択（Gemini-pro）
    model = genai.GenerativeModel('gemini-2.5-flash')

    # プロンプト（あなたの指定内容）
    prompt = """
この画像から、グループ名、メンバー名、担当カラーの情報を抽出してテーブルを作成し、csvファイルを出力してください

・形式：
　・カンマ区切り
　・ヘッダ：最初の行に、列名として　「名前,カラー」と記載
　・メンバー名：漢字、スペース無し
　・メンバーカラー：文字列 
・人数：全メンバー分
・ファイル名：member_colors_[グループ名].csv
"""

    # Geminiリクエスト（v1beta形式）
    payload = {
        "contents": [
            {
                "parts": [
                    { "text": prompt },
                    {
                        "inline_data": {
                            "mime_type": "image/png",
                            "data": image_base64
                        }
                    }
                ]
            }
        ]
    }
    headers = { "Content-Type": "application/json" }

    print("\nGemini APIに問い合わせ中...")
    res = requests.post(API_URL, headers=headers, json=payload)
    print("res:",res)
    if res.status_code != 200:
        return_text = f"エラー: {res.status_code}\n{res.text}"
        print("return_text:",return_text)
        return return_text

    reply_text = res.json()["candidates"][0]["content"]["parts"][0]["text"]
    print("\nGemini応答:\n", reply_text)

    # === Gemini応答のCSVパース ===
    lines = reply_text.strip().splitlines()
    rows = [line.strip().split(",") for line in lines if "," in line and "名前" not in line]


    # 不正な行（ヘッダやコメントなど）を除去：2列のみ残す
    rows = [row for row in rows if isinstance(row, list) and len(row) == 2]


    # グループ名取得
    group_match = re.search(r'member_colors_(\S+)\.csv', reply_text)
    group_name = group_match.group(1) if group_match else "group"


    # ディレクトリ準備
    base_dir = os.path.join(os.path.dirname(image_path), "..", "..", "tables")


    # === CSV出力（顔画像処理なし） ===
    csv_filename = f"member_colors_{group_name}.csv"
    csv_path = os.path.join(base_dir, csv_filename)

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["名前", "カラー"])  # 顔画像列は不要
        for name, color in rows:
            writer.writerow([name, color])

    print(f"\n$2705 CSV出力完了: {csv_path}")
    return {
        "group_name": group_name,
        "members": [{"name": name, "color": color} for name, color in rows]
    }


