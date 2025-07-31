#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RCCM試験システム - 単純化版 (Phase 1)
2-3週間治らない問題の根本解決版
専門家推奨手法：最小限・確実・日本語統一

ウルトラシンク原則：
- 絶対に嘘をつかない
- 推測による実装なし  
- 確実に動作する最小限機能
"""

from flask import Flask, render_template_string, request, session, redirect, url_for
import pandas as pd
import os
import random
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'rccm-simple-key-2025'  # 本番では環境変数使用

# 専門家推奨：確実に特定された日本語カテゴリ（完全版）
DEPARTMENT_CATEGORIES = [
    "道路",
    "河川、砂防及び海岸・海洋",  
    "都市計画及び地方計画",
    "造園",
    "建設環境", 
    "鋼構造及びコンクリート",
    "土質及び基礎",
    "施工計画、施工設備及び積算",
    "上水道及び工業用水道",
    "森林土木",
    "農業土木",
    "トンネル"
]

# 確実に存在する年度リスト
AVAILABLE_YEARS = [2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019]

def load_csv_safe(file_path):
    """
    専門家推奨：安全なCSV読み込み（複数エンコーディング対応）
    絶対に嘘をつかない：例外時はNoneを返す
    """
    if not os.path.exists(file_path):
        print(f"ERROR: ファイルが存在しません: {file_path}")
        return None
    
    # 専門家推奨：複数エンコーディング試行順序
    encodings_to_try = ['utf-8', 'utf-8-sig', 'shift_jis', 'cp932', 'euc-jp']
    
    for encoding in encodings_to_try:
        try:
            df = pd.read_csv(file_path, encoding=encoding)
            print(f"OK: {file_path} 読み込み成功 ({encoding})")
            return df
        except Exception as e:
            print(f"WARNING: {file_path} エンコーディング {encoding} 失敗: {e}")
            continue
    
    print(f"ERROR: {file_path} すべてのエンコーディング失敗")
    return None

def get_questions_by_category(category):
    """
    カテゴリに応じた問題取得（確実版）
    """
    if category == "共通":
        # 4-1.csv（共通部門）
        df = load_csv_safe("data/4-1.csv")
        if df is not None:
            return df.to_dict('records')
    else:
        # 4-2ファイル群から該当カテゴリをフィルタ
        all_questions = []
        for year in AVAILABLE_YEARS:
            file_path = f"data/4-2_{year}.csv"
            df = load_csv_safe(file_path)
            if df is not None:
                # 完全一致フィルタ（専門家推奨）
                filtered = df[df['category'] == category]
                if len(filtered) > 0:
                    all_questions.extend(filtered.to_dict('records'))
        
        if all_questions:
            print(f"OK: カテゴリ '{category}' で {len(all_questions)} 問題取得")
            return all_questions
    
    print(f"ERROR: カテゴリ '{category}' の問題が見つかりません")
    return []

def get_questions_by_year(year):
    """
    年度別問題取得（確実版）
    """
    if year not in AVAILABLE_YEARS:
        print(f"ERROR: 無効な年度です: {year}")
        return [], []
    
    file_path = f"data/4-2_{year}.csv"
    df = load_csv_safe(file_path)
    
    if df is not None:
        questions = df.to_dict('records')
        categories = sorted(df['category'].unique())
        print(f"OK: {year}年度 {len(questions)}問題、{len(categories)}カテゴリ取得")
        return questions, categories
    
    print(f"ERROR: {year}年度のファイルが読み込めません")
    return [], []

# HTML テンプレート（最小限）
HOME_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>RCCM試験システム（単純化版）</title>
    <meta charset="utf-8">
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .category-list { list-style: none; padding: 0; }
        .category-item { margin: 10px 0; }
        .category-link { 
            display: block; 
            padding: 15px; 
            background: #f0f0f0; 
            text-decoration: none; 
            color: #333;
            border-radius: 5px;
        }
        .category-link:hover { background: #e0e0e0; }
        .common-category { background: #d4edda; }
        .year-category { background: #fff3cd; }
        .section-header { 
            background: #343a40; 
            color: white; 
            padding: 10px; 
            margin: 20px 0 10px 0; 
            border-radius: 5px;
        }
    </style>
</head>
<body>
    <h1>RCCM試験システム（単純化版）</h1>
    <p><strong>ウルトラシンク版</strong> - 2-3週間治らない問題の根本解決</p>
    
    <div class="section-header">
        <h2>📚 共通部門</h2>
    </div>
    <ul class="category-list">
        <li class="category-item">
            <a href="/quiz/共通" class="category-link common-category">
                共通部門（基礎科目）
            </a>
        </li>
    </ul>
    
    <div class="section-header">
        <h2>🏗️ 専門部門（全年度統合）</h2>
    </div>
    <ul class="category-list">
        {% for category in categories %}
        <li class="category-item">
            <a href="/quiz/{{ category }}" class="category-link">
                {{ category }}
            </a>
        </li>
        {% endfor %}
    </ul>
    
    <div class="section-header">
        <h2>📅 年度別選択</h2>
    </div>
    <ul class="category-list">
        {% for year in years %}
        <li class="category-item">
            <a href="/year/{{ year }}" class="category-link year-category">
                {{ year }}年度の問題
            </a>
        </li>
        {% endfor %}
    </ul>
    
    <hr>
    <p><small>
        作成時刻: {{ timestamp }}<br>
        データファイル: 4-1.csv（共通）+ 4-2_2008-2019.csv（専門）<br>
        対応年度: {{ years|length }}年分 / 対応部門: {{ categories|length + 1 }}部門
    </small></p>
</body>
</html>
'''

QUIZ_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>問題 {{ current_num }}/{{ total_num }} - {{ category }}</title>
    <meta charset="utf-8">
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .question-header { background: #f8f9fa; padding: 20px; margin-bottom: 20px; }
        .question-text { font-size: 1.1em; margin-bottom: 20px; }
        .options { list-style: none; padding: 0; }
        .option { margin: 10px 0; }
        .option input { margin-right: 10px; }
        .submit-btn { 
            background: #007bff; 
            color: white; 
            padding: 15px 30px; 
            border: none; 
            border-radius: 5px; 
            font-size: 1.1em;
            cursor: pointer;
        }
        .submit-btn:hover { background: #0056b3; }
    </style>
</head>
<body>
    <div class="question-header">
        <h1>{{ category }}</h1>
        <h2>問題 {{ current_num }} / {{ total_num }}</h2>
    </div>
    
    <div class="question-text">
        <p>{{ question.question }}</p>
    </div>
    
    <form method="POST">
        <ul class="options">
            <li class="option">
                <input type="radio" name="answer" value="A" id="option_a" required>
                <label for="option_a">A. {{ question.option_a }}</label>
            </li>
            <li class="option">
                <input type="radio" name="answer" value="B" id="option_b" required>
                <label for="option_b">B. {{ question.option_b }}</label>
            </li>
            <li class="option">
                <input type="radio" name="answer" value="C" id="option_c" required>
                <label for="option_c">C. {{ question.option_c }}</label>
            </li>
            <li class="option">
                <input type="radio" name="answer" value="D" id="option_d" required>
                <label for="option_d">D. {{ question.option_d }}</label>
            </li>
        </ul>
        
        <input type="submit" value="回答する" class="submit-btn">
    </form>
    
    <hr>
    <p><a href="/">← トップページに戻る</a></p>
</body>
</html>
'''

RESULT_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>結果 - {{ category }}</title>
    <meta charset="utf-8">
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .result-header { background: #d4edda; padding: 20px; margin-bottom: 20px; text-align: center; }
        .score { font-size: 2em; font-weight: bold; color: #155724; }
        .details { margin: 20px 0; }
        .retry-btn { 
            background: #28a745; 
            color: white; 
            padding: 15px 30px; 
            text-decoration: none; 
            border-radius: 5px; 
            display: inline-block;
            margin: 10px;
        }
        .home-btn { 
            background: #6c757d; 
            color: white; 
            padding: 15px 30px; 
            text-decoration: none; 
            border-radius: 5px; 
            display: inline-block;
            margin: 10px;
        }
    </style>
</head>
<body>
    <div class="result-header">
        <h1>{{ category }} - 結果</h1>
        <div class="score">{{ correct_count }} / {{ total_count }} 問正解</div>
        <p>正答率: {{ percentage }}%</p>
    </div>
    
    <div class="details">
        <h3>詳細結果</h3>
        <p>実施日時: {{ completed_at }}</p>
        <p>所要時間: 約{{ duration }}分</p>
    </div>
    
    <div>
        <a href="/quiz/{{ category }}" class="retry-btn">もう一度挑戦</a>
        <a href="/" class="home-btn">トップページ</a>
    </div>
</body>
</html>
'''

YEAR_SELECT_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>{{ year }}年度の問題 - カテゴリ選択</title>
    <meta charset="utf-8">
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .year-header { 
            background: #fff3cd; 
            padding: 20px; 
            margin-bottom: 20px; 
            text-align: center;
            border-radius: 5px;
        }
        .category-list { list-style: none; padding: 0; }
        .category-item { margin: 10px 0; }
        .category-link { 
            display: block; 
            padding: 15px; 
            background: #f8f9fa; 
            text-decoration: none; 
            color: #333;
            border-radius: 5px;
            border-left: 4px solid #ffc107;
        }
        .category-link:hover { background: #e2e6ea; }
        .back-btn { 
            background: #6c757d; 
            color: white; 
            padding: 10px 20px; 
            text-decoration: none; 
            border-radius: 5px; 
            display: inline-block;
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <a href="/" class="back-btn">← トップページに戻る</a>
    
    <div class="year-header">
        <h1>{{ year }}年度の問題</h1>
        <p>利用可能なカテゴリ: {{ categories|length }}部門</p>
    </div>
    
    <ul class="category-list">
        {% for category in categories %}
        <li class="category-item">
            <a href="/quiz-year/{{ year }}/{{ category }}" class="category-link">
                {{ category }}
            </a>
        </li>
        {% endfor %}
    </ul>
    
    <hr>
    <p><small>
        {{ year }}年度データ: {{ total_questions }}問題<br>
        作成時刻: {{ timestamp }}
    </small></p>
</body>
</html>
'''

@app.route('/')
def home():
    """ホームページ：部門選択"""
    return render_template_string(HOME_TEMPLATE, 
                                  categories=DEPARTMENT_CATEGORIES,
                                  years=AVAILABLE_YEARS,
                                  timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

@app.route('/quiz/<category>')
def start_quiz(category):
    """クイズ開始：10問ランダム選択"""
    
    # カテゴリ検証
    valid_categories = ["共通"] + DEPARTMENT_CATEGORIES
    if category not in valid_categories:
        return f"エラー: 無効なカテゴリです: {category}", 400
    
    # 問題取得
    questions = get_questions_by_category(category)
    if not questions:
        return f"エラー: カテゴリ '{category}' の問題が見つかりません", 404
    
    # 10問ランダム選択
    selected_questions = random.sample(questions, min(10, len(questions)))
    
    # セッション初期化
    session['quiz_category'] = category
    session['quiz_questions'] = selected_questions
    session['quiz_current'] = 0
    session['quiz_answers'] = []
    session['quiz_start_time'] = datetime.now().isoformat()
    
    print(f"OK: クイズ開始 - カテゴリ: {category}, 問題数: {len(selected_questions)}")
    
    # 最初の問題表示
    return show_question()

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    """問題表示・回答処理"""
    
    if request.method == 'POST':
        # 回答処理
        answer = request.form.get('answer')
        if answer:
            session['quiz_answers'].append(answer)
            session['quiz_current'] += 1
        
        # 次の問題 or 結果画面
        if session['quiz_current'] >= len(session.get('quiz_questions', [])):
            return redirect(url_for('result'))
        else:
            return show_question()
    
    else:
        # GET: 問題表示
        return show_question()

def show_question():
    """現在の問題を表示"""
    
    questions = session.get('quiz_questions', [])
    current = session.get('quiz_current', 0)
    category = session.get('quiz_category', '')
    
    if current >= len(questions):
        return redirect(url_for('result'))
    
    question = questions[current]
    
    return render_template_string(QUIZ_TEMPLATE,
                                  question=question,
                                  current_num=current + 1,
                                  total_num=len(questions),
                                  category=category)

@app.route('/year/<int:year>')
def year_select(year):
    """年度別カテゴリ選択"""
    
    # 年度検証
    if year not in AVAILABLE_YEARS:
        return f"エラー: 無効な年度です: {year}", 400
    
    # 年度別問題とカテゴリ取得
    questions, categories = get_questions_by_year(year)
    
    if not questions or not categories:
        return f"エラー: {year}年度の問題が見つかりません", 404
    
    return render_template_string(YEAR_SELECT_TEMPLATE,
                                  year=year,
                                  categories=categories,
                                  total_questions=len(questions),
                                  timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

@app.route('/quiz-year/<int:year>/<category>')
def start_quiz_by_year(year, category):
    """年度・カテゴリ指定でクイズ開始"""
    
    # 年度検証
    if year not in AVAILABLE_YEARS:
        return f"エラー: 無効な年度です: {year}", 400
    
    # 年度別問題取得
    questions, categories = get_questions_by_year(year)
    
    if not questions:
        return f"エラー: {year}年度の問題が見つかりません", 404
    
    # カテゴリフィルタ
    category_questions = [q for q in questions if q.get('category') == category]
    
    if not category_questions:
        return f"エラー: {year}年度の'{category}'カテゴリに問題がありません", 404
    
    # 10問ランダム選択
    selected_questions = random.sample(category_questions, min(10, len(category_questions)))
    
    # セッション初期化
    session['quiz_category'] = f"{category}（{year}年度）"
    session['quiz_questions'] = selected_questions
    session['quiz_current'] = 0
    session['quiz_answers'] = []
    session['quiz_start_time'] = datetime.now().isoformat()
    
    print(f"OK: 年度別クイズ開始 - {year}年度 {category}, 問題数: {len(selected_questions)}")
    
    # 最初の問題表示
    return show_question()

@app.route('/result')
def result():
    """結果表示"""
    
    questions = session.get('quiz_questions', [])
    answers = session.get('quiz_answers', [])
    category = session.get('quiz_category', '')
    start_time = session.get('quiz_start_time', '')
    
    if not questions or not answers:
        return redirect(url_for('home'))
    
    # 正答数計算
    correct_count = 0
    for i, question in enumerate(questions):
        if i < len(answers):
            if answers[i] == question.get('correct_answer'):
                correct_count += 1
    
    total_count = len(questions)
    percentage = round((correct_count / total_count) * 100, 1) if total_count > 0 else 0
    
    # 所要時間計算
    try:
        start_dt = datetime.fromisoformat(start_time)
        duration = round((datetime.now() - start_dt).total_seconds() / 60, 1)
    except:
        duration = "不明"
    
    return render_template_string(RESULT_TEMPLATE,
                                  category=category,
                                  correct_count=correct_count,
                                  total_count=total_count,
                                  percentage=percentage,
                                  completed_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                  duration=duration)

if __name__ == '__main__':
    print("=" * 60)
    print("RCCM試験システム（単純化版）起動")
    print("ウルトラシンク - 2-3週間治らない問題の根本解決版")
    print("=" * 60)
    
    # データファイル存在確認
    print("\nデータファイル確認:")
    common_file = "data/4-1.csv"
    if os.path.exists(common_file):
        print(f"OK: {common_file}")
    else:
        print(f"ERROR: {common_file} が見つかりません")
    
    for year in AVAILABLE_YEARS:
        file_path = f"data/4-2_{year}.csv"
        if os.path.exists(file_path):
            print(f"OK: {file_path}")
        else:
            print(f"WARNING: {file_path} が見つかりません")
    
    print(f"\n対応カテゴリ数: {len(DEPARTMENT_CATEGORIES)} + 1（共通）")
    print(f"対応年度数: {len(AVAILABLE_YEARS)}")
    print("\nサーバー起動中...")
    
    # 本番環境対応：環境変数からポート取得、デフォルトは5007
    port = int(os.environ.get('PORT', 5007))
    host = '0.0.0.0' if 'PORT' in os.environ else '127.0.0.1'
    debug_mode = 'PORT' not in os.environ
    
    app.run(debug=debug_mode, host=host, port=port)