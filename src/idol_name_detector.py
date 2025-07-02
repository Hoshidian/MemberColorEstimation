import google.generativeai as genai
from PIL import Image
import os
import sys


def analyze_image_with_gemini(image_path: str, group_name: str):
    """
    指定された画像をGeminiモデルで分析し、その内容を説明します。

    Args:
        image_path (str): 分析する画像のパス。

    Returns:
        str: 画像の内容に関するGeminiモデルからの説明。
             エラーが発生した場合は、エラーメッセージを返します。
    """
    try:
        # 画像ファイルを読み込む
        img = Image.open(image_path)

        # Geminiモデルを初期化（'gemini-pro-vision'は画像とテキストの両方を扱えるモデル）
       #API_KEY = ""  # ここに取得したAPIキーを貼り付けてください
        API_KEY=os.getenv("GEMINI_API_KEY")
        genai.configure(api_key=API_KEY)

        # モデルの選択（Gemini-pro）
        model = genai.GenerativeModel('gemini-2.5-flash')

        # プロンプトと画像をモデルに渡す
        # ここでは「この画像に何が写っていますか？」と尋ねています
        #response = model.generate_content(["AKB48に所属するこの人物の名前は？回答形式は「氏名：XXX グループ名：XXX」の形式とすること(XXXに回答結果を示すこと)。過去に所属していたメンバーも含むものとする", img])
        prompt = f"この画像に写っている{group_name}の有名人の名前は何ですか？"
        response = model.generate_content([prompt, img],
                                          generation_config=genai.types.GenerationConfig(temperature=0.0) 
        ) 
        


        # 回答を返す
        return response.text

    except Exception as e:
        return f"画像の分析中にエラーが発生しました: {e}"


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("使い方: python idol_name_identifier.py <グループ名> <画像ファイルのパス>")
        print("例: python idol_name_identifier.py 乃木坂46 work/image.png")
        sys.exit(1)

    group_name = sys.argv[1]
    image_path = sys.argv[2]

    if not os.path.exists(image_path):
        print(f"エラー: 画像ファイルが見つかりません → {image_path}")
        sys.exit(1)

    print(f"\n'{group_name}' のアイドル候補を分析中（画像：{image_path}）...\n")
    result = analyze_image_with_gemini(image_path, group_name)
    print("--- Geminiの回答 ---")
    print(result)
    print("---------------------")



