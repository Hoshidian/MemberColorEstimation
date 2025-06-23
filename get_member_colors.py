import argparse
import csv
import os
import re
import sys
import google.generativeai as genai
from typing import List, Tuple

def convert_japanese_to_alphabet(japanese_name: str) -> str:
    """
    日本語のグループ名をアルファベットに変換する
    簡易的な変換（実際の使用ではより詳細な変換が必要）
    """
    # 一般的なアイドルグループ名の変換マッピング
    conversion_map = {
        '乃木坂46': 'nogizaka46',
        '欅坂46': 'keyakizaka46',
        '櫻坂46': 'sakurazaka46',
        '日向坂46': 'hinatazaka46',
        'AKB48': 'akb48',
        'SKE48': 'ske48',
        'NMB48': 'nmb48',
        'HKT48': 'hkt48',
        'NGT48': 'ngt48',
        'STU48': 'stu48',
        'JKT48': 'jkt48',
        'BNK48': 'bnk48',
        'MNL48': 'mnl48',
        'AKB48 Team TP': 'akb48teamtp',
        'AKB48 Team SH': 'akb48teamsh',
        'AKB48 Team 8': 'akb48team8',
        'モーニング娘。': 'morningmusume',
        'ANGERME': 'angerme',
        'Juice=Juice': 'juicejuice',
        'つばきファクトリー': 'tsubakifactory',
        'BEYOOOOONDS': 'beyooooonds',
        'OCHA NORMA': 'ochanorma',
        'Hello! Project': 'helloproject',
        'Perfume': 'perfume',
        'BABYMETAL': 'babymetal',
        'BAND-MAID': 'bandmaid',
        'SCANDAL': 'scandal',
        'ONE OK ROCK': 'oneokrock',
        'RADWIMPS': 'radwimps',
        'BUMP OF CHICKEN': 'bumpofchicken',
        'GReeeeN': 'greeeen',
        'Mr.Children': 'mrchildren',
        'サザンオールスターズ': 'southernallstars',
        'SMAP': 'smap',
        '嵐': 'arashi',
        'KinKi Kids': 'kinkikids',
        'V6': 'v6',
        'TOKIO': 'tokio',
        'NEWS': 'news',
        '関ジャニ∞': 'kanjani8',
        'KAT-TUN': 'kattun',
        'Hey! Say! JUMP': 'heysayjump',
        'Kis-My-Ft2': 'kismyft2',
        'Sexy Zone': 'sexyzone',
        'A.B.C-Z': 'abcz',
        'ジャニーズWEST': 'johnnyswest',
        'King & Prince': 'kingandprince',
        'SixTONES': 'sixtones',
        'Snow Man': 'snowman',
        'なにわ男子': 'naniwadanshi',
        'Travis Japan': 'travisjapan',
        'IMPACTors': 'impactors',
        '美 少年': 'bishonen',
        'Lil かんさい': 'lilkansai',
        'HiHi Jets': 'hihijets',
        '少年忍者': 'shonen_ninja',
        '7 MEN 侍': '7mensamurai',
        'BALLISTIK BOYZ': 'ballistikboyz',
        'FANTASTICS': 'fantastics',
        'THE RAMPAGE': 'therampage',
        'GENERATIONS': 'generations',
        'EXILE': 'exile',
        '三代目 J SOUL BROTHERS': 'sandaime_jsoulbrothers',
        'E-girls': 'egirls',
        'Flower': 'flower',
        'Happiness': 'happiness',
        'SudannaYuzuYully': 'sudannayuzuyully',
        'Girls²': 'girls2',
        'BOYS AND MEN': 'boysandmen',
        'BOYS AND MEN研究生': 'boysandmen_kenkyusei',
        '祭nine.': 'matsurinine',
        '超特急': 'chotokkyu',
        'Da-iCE': 'daice',
        'Lead': 'lead',
        'w-inds.': 'winds',
        'FLAME': 'flame',
        'Folder5': 'folder5',
        'AAA': 'aaa',
        'V6': 'v6',
        'TOKIO': 'tokio',
        'NEWS': 'news',
        '関ジャニ∞': 'kanjani8',
        'KAT-TUN': 'kattun',
        'Hey! Say! JUMP': 'heysayjump',
        'Kis-My-Ft2': 'kismyft2',
        'Sexy Zone': 'sexyzone',
        'A.B.C-Z': 'abcz',
        'ジャニーズWEST': 'johnnyswest',
        'King & Prince': 'kingandprince',
        'SixTONES': 'sixtones',
        'Snow Man': 'snowman',
        'なにわ男子': 'naniwadanshi',
        'Travis Japan': 'travisjapan',
        'IMPACTors': 'impactors',
        '美 少年': 'bishonen',
        'Lil かんさい': 'lilkansai',
        'HiHi Jets': 'hihijets',
        '少年忍者': 'shonen_ninja',
        '7 MEN 侍': '7mensamurai',
        'BALLISTIK BOYZ': 'ballistikboyz',
        'FANTASTICS': 'fantastics',
        'THE RAMPAGE': 'therampage',
        'GENERATIONS': 'generations',
        'EXILE': 'exile',
        '三代目 J SOUL BROTHERS': 'sandaime_jsoulbrothers',
        'E-girls': 'egirls',
        'Flower': 'flower',
        'Happiness': 'happiness',
        'SudannaYuzuYully': 'sudannayuzuyully',
        'Girls²': 'girls2',
        'BOYS AND MEN': 'boysandmen',
        'BOYS AND MEN研究生': 'boysandmen_kenkyusei',
        '祭nine.': 'matsurinine',
        '超特急': 'chotokkyu',
        'Da-iCE': 'daice',
        'Lead': 'lead',
        'w-inds.': 'winds',
        'FLAME': 'flame',
        'Folder5': 'folder5',
        'AAA': 'aaa'
    }
    
    # マッピングに存在する場合は変換
    if japanese_name in conversion_map:
        return conversion_map[japanese_name]
    
    # マッピングに存在しない場合は簡易変換
    # ひらがな・カタカナを削除し、英数字のみを残す
    alphabet_name = re.sub(r'[あ-んア-ン]', '', japanese_name)
    # 特殊文字を削除
    alphabet_name = re.sub(r'[^\w\s]', '', alphabet_name)
    # スペースを削除
    alphabet_name = re.sub(r'\s+', '', alphabet_name)
    # 小文字に変換
    alphabet_name = alphabet_name.lower()
    
    return alphabet_name if alphabet_name else 'unknown_group'

def get_member_colors_from_gemini(group_name: str, api_key: str) -> List[Tuple[str, str]]:
    """
    Gemini APIを使用してメンバー名とメンバーカラーの対応表を取得
    """
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash")

    prompt = f"""{group_name}のメンバー名とメンバーカラーの対応表を作成し、csvファイルを添付して出力してください
・形式：
　・カンマ区切り
　・ヘッダ：最初の行に、列名として　「名前,カラー」と記載
　・メンバー名：漢字、スペース無し
　・メンバーカラー：文字列。複数色ある場合は、色×色という記載方式。
・人数：全メンバー分"""

    try:
        response = model.generate_content(prompt)
        content = response.text
        # CSVデータを抽出
        csv_data = extract_csv_from_response(content)
        if not csv_data:
            print("警告: Geminiの応答からCSVデータを抽出できませんでした。")
            print("応答内容:", content)
            return []
        return csv_data
    except Exception as e:
        print(f"Gemini API呼び出しエラー: {e}")
        return []

def extract_csv_from_response(response: str) -> List[Tuple[str, str]]:
    """
    Geminiの応答からCSVデータを抽出
    """
    lines = response.strip().split('\n')
    csv_data = []
    
    for line in lines:
        # CSV形式の行を探す（カンマ区切りで2つの要素がある行）
        if ',' in line and line.count(',') == 1:
            parts = line.split(',')
            if len(parts) == 2:
                name = parts[0].strip()
                color = parts[1].strip()
                
                # ヘッダー行をスキップ
                if name.lower() in ['名前', 'name', 'メンバー名', 'member']:
                    continue
                
                # 空の行をスキップ
                if name and color:
                    csv_data.append((name, color))
    
    return csv_data

def save_to_csv(data: List[Tuple[str, str]], filepath: str):
    """
    データをCSVファイルに保存
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['名前', 'カラー'])  # ヘッダー
        writer.writerows(data)
    
    print(f"CSVファイルを保存しました: {filepath}")

def main():
    parser = argparse.ArgumentParser(description='アイドルグループのメンバー名とメンバーカラーの対応表を取得')
    parser.add_argument('group_name', help='アイドルグループ名（日本語）')
    parser.add_argument('--api-key', help='Google Gemini APIキー（環境変数GEMINI_API_KEYからも取得可能）')
    args = parser.parse_args()
    # APIキーの取得
    api_key = args.api_key or os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("エラー: Google Gemini APIキーが必要です。")
        print("使用方法:")
        print("1. 環境変数GEMINI_API_KEYを設定する")
        print("2. --api-keyオプションで指定する")
        sys.exit(1)
    group_name = args.group_name
    group_name_alphabet = convert_japanese_to_alphabet(group_name)
    print(f"グループ名: {group_name}")
    print(f"アルファベット変換: {group_name_alphabet}")
    print("Gemini APIからメンバー情報を取得中...")
    # Geminiからデータを取得
    member_data = get_member_colors_from_gemini(group_name, api_key)
    if not member_data:
        print("エラー: メンバー情報を取得できませんでした。")
        sys.exit(1)
    print(f"取得したメンバー数: {len(member_data)}")
    # CSVファイルに保存
    csv_filepath = f"./tables/member_colors_{group_name_alphabet}.csv"
    save_to_csv(member_data, csv_filepath)
    # 取得したデータを表示
    print("\n取得したメンバー情報:")
    for name, color in member_data:
        print(f"  {name}: {color}")

if __name__ == "__main__":
    main() 