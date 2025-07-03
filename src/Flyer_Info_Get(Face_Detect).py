#!/usr/bin/env python
# coding: utf-8

# In[1]:


import base64
import requests
import tkinter as tk
from tkinter import filedialog
import os
import csv
import re
from ultralytics import YOLO
import cv2

# ======== YOLOv8 face設定 ========
model_path = "yolov8n-face-lindevs.pt"          # 学習済みYOLOv8 faceモデル
conf_threshold = 0.4                    # 信頼度の閾値（調整可能）
max_faces = 10                          # 検出する最大人数
# ======================


# In[2]:


# === 画像選択ダイアログ ===
root = tk.Tk()
root.withdraw()
image_path = filedialog.askopenfilename(title="画像ファイルを選択してください")
if not image_path:
    raise Exception("画像ファイルが選択されませんでした。")


# In[3]:


# Base64エンコード
with open(image_path, "rb") as f:
    image_bytes = f.read()
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")


# In[4]:


# APIキーとエンドポイント
gemini_api_key = os.environ.get("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("⚠️ 環境変数 GEMINI_API_KEY が設定されていません。")
#gemini_api_key = input("Gemini APIキーを入力してください: ").strip()
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_api_key}"


# In[5]:


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


# In[6]:


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
if res.status_code != 200:
    print("エラー:", res.status_code)
    print(res.text)
    exit()

reply_text = res.json()["candidates"][0]["content"]["parts"][0]["text"]
print("\nGemini応答:\n", reply_text)


# In[7]:


# === Gemini応答のCSVパース ===
lines = reply_text.strip().splitlines()
rows = [line.strip().split(",") for line in lines if "," in line and "名前" not in line]


# In[8]:


# 不正な行（ヘッダやコメントなど）を除去：2列のみ残す
rows = [row for row in rows if isinstance(row, list) and len(row) == 2]


# In[9]:


# グループ名取得
group_match = re.search(r'member_colors_(\S+)\.csv', reply_text)
group_name = group_match.group(1) if group_match else "group"


# In[10]:


# モデル読み込み
model = YOLO(model_path)


# In[11]:


# 画像読み込み
image = cv2.imread(image_path)
if image is None:
    raise FileNotFoundError(f"画像が読み込めません: {image_path}")


# In[12]:


# 顔検出（推論実行）
results = model(image)[0]
boxes = [b for b in results.boxes if b.conf >= conf_threshold]
boxes_sorted = sorted(boxes, key=lambda b: b.xyxy[0][0])  # 左→右順で並び替え


# In[13]:


# ディレクトリ準備
csv_dir = os.path.dirname(image_path)
face_dir = os.path.join(csv_dir, f"member_faces_{group_name}")
os.makedirs(face_dir, exist_ok=True)


# In[14]:


# === CSV出力 ===
csv_filename = f"member_colors_{group_name}.csv"
csv_path = os.path.join(csv_dir, csv_filename)

with open(csv_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["名前", "カラー"]) 
    for name, color in rows:
        writer.writerow([name, color])

print(f"\n✅ CSV出力完了: {csv_path}")


# In[15]:


# 顔をトリミングして保存
def sanitize_filename(name):
    return re.sub(r'[^\w\u3040-\u30ff\u4e00-\u9fff-]', '_', name)

for i, box in enumerate(boxes_sorted[:len(rows)]):
    x1, y1, x2, y2 = map(int, box.xyxy[0])
    face = image[y1:y2, x1:x2]
    name = rows[i][0]
    filename = sanitize_filename(name) + ".jpg"
    save_path = os.path.join(face_dir, filename)
    cv2.imwrite(save_path, face)
    print(f"✅ 保存: {filename}")


# In[ ]:




