# -*- coding: utf-8 -*-
"""
Enhanced HTML Response Analysis - Detailed Production Investigation
フィードバックページ検出失敗の根本原因調査
Beyond Surface Level Testing - Comprehensive HTML Analysis
"""

import requests
import json
import time
from datetime import datetime
from bs4 import BeautifulSoup
import os

class EnhancedHTMLResponseAnalyzer:
    """
    Enhanced HTML Response Analysis
    Deep investigation of feedback page detection failures
    """
    
    def __init__(self):
        self.production_url = "https://rccm-quiz-2025.onrender.com"
        self.analysis_results = {
            "timestamp": datetime.now().isoformat(),
            "analysis_type": "ENHANCED_HTML_RESPONSE_ANALYSIS",
            "question_type_responses": {},
            "feedback_detection_analysis": {},
            "comparative_analysis": {}
        }
    
    def capture_detailed_response(self, department, question_type, test_name):
        """
        Capture detailed HTML response for analysis
        """
        print(f"\n=== {test_name} HTML Response Analysis ===")
        
        session = requests.Session()
        response_data = {
            "test_name": test_name,
            "department": department,
            "question_type": question_type,
            "initialization": {},
            "post_response": {},
            "html_analysis": {}
        }
        
        try:
            # Phase 1: Initialize exam
            exam_url = f"{self.production_url}/exam?department={department}&question_type={question_type}&count=10"
            response = session.get(exam_url, timeout=30)
            
            print(f"  初期化ステータス: {response.status_code}")
            response_data["initialization"]["status_code"] = response.status_code
            
            if response.status_code != 200:
                print(f"  [ERROR] 初期化失敗")
                return response_data
            
            soup = BeautifulSoup(response.text, 'html.parser')
            csrf_token = soup.find('input', {'name': 'csrf_token'})
            qid_input = soup.find('input', {'name': 'qid'})
            
            if not csrf_token or not qid_input:
                print(f"  [ERROR] トークン不足")
                response_data["initialization"]["missing_tokens"] = True
                return response_data
            
            csrf_value = csrf_token.get('value')
            qid_value = qid_input.get('value')
            
            print(f"  QID: {qid_value}")
            response_data["initialization"]["qid"] = qid_value
            response_data["initialization"]["csrf_present"] = True
            
            # Save initial HTML for analysis
            initial_html_file = f"{test_name}_initial.html"
            with open(initial_html_file, 'w', encoding='utf-8') as f:
                f.write(response.text)
            print(f"  初期HTMLファイル保存: {initial_html_file}")
            
            # Phase 2: Submit POST request
            post_data = {
                'csrf_token': csrf_value,
                'qid': qid_value,
                'answer': 'A',
                'elapsed': 45
            }
            
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Referer': exam_url,
                'Origin': self.production_url,
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            print(f"  POST送信中...")
            post_response = session.post(f"{self.production_url}/exam", 
                                       data=post_data, 
                                       headers=headers,
                                       timeout=30)
            
            print(f"  POSTステータス: {post_response.status_code}")
            response_data["post_response"]["status_code"] = post_response.status_code
            response_data["post_response"]["content_length"] = len(post_response.text)
            
            # Save POST response HTML for detailed analysis
            post_html_file = f"{test_name}_post_response.html"
            with open(post_html_file, 'w', encoding='utf-8') as f:
                f.write(post_response.text)
            print(f"  POST応答HTMLファイル保存: {post_html_file}")
            
            # Phase 3: Detailed HTML Analysis
            if post_response.status_code == 200:
                feedback_soup = BeautifulSoup(post_response.text, 'html.parser')
                
                # Multiple feedback detection methods
                feedback_indicators = {
                    "正解_text": "正解" in post_response.text,
                    "不正解_text": "不正解" in post_response.text,
                    "feedback_card_class": bool(feedback_soup.find('div', class_='feedback-card')),
                    "あなたの解答_text": "あなたの解答:" in post_response.text,
                    "解答_text": "解答:" in post_response.text,
                    "解説_text": "解説:" in post_response.text,
                    "feedback_div": bool(feedback_soup.find('div', class_='feedback')),
                    "result_div": bool(feedback_soup.find('div', class_='result')),
                    "answer_div": bool(feedback_soup.find('div', class_='answer'))
                }
                
                response_data["html_analysis"]["feedback_indicators"] = feedback_indicators
                
                # Check for next question link
                next_link = feedback_soup.find('a', href=lambda x: x and 'next=1' in x)
                response_data["html_analysis"]["next_link_present"] = bool(next_link)
                if next_link:
                    response_data["html_analysis"]["next_link_href"] = next_link.get('href')
                
                # Extract key HTML elements
                title_tag = feedback_soup.find('title')
                response_data["html_analysis"]["page_title"] = title_tag.text if title_tag else "NO_TITLE"
                
                # Check for error messages
                error_indicators = {
                    "error_class": bool(feedback_soup.find(class_='error')),
                    "alert_class": bool(feedback_soup.find(class_='alert')),
                    "内部エラー_text": "内部エラー" in post_response.text,
                    "エラー_text": "エラー" in post_response.text,
                    "500_error": "500" in post_response.text,
                    "400_error": "400" in post_response.text
                }
                
                response_data["html_analysis"]["error_indicators"] = error_indicators
                
                # Text content analysis
                text_content = post_response.text
                response_data["html_analysis"]["contains_japanese"] = any('\u3040' <= char <= '\u309F' or '\u30A0' <= char <= '\u30FF' or '\u4E00' <= char <= '\u9FAF' for char in text_content)
                response_data["html_analysis"]["total_text_length"] = len(text_content)
                
                # Sample text for manual inspection
                clean_text = ' '.join(text_content.split())
                response_data["html_analysis"]["text_sample"] = clean_text[:500] + "..." if len(clean_text) > 500 else clean_text
                
                # Final feedback detection verdict
                has_any_feedback = any(feedback_indicators.values())
                response_data["html_analysis"]["feedback_detected"] = has_any_feedback
                
                print(f"  フィードバック検出結果:")
                for indicator, detected in feedback_indicators.items():
                    status = "検出" if detected else "未検出"
                    print(f"    {indicator}: {status}")
                
                print(f"  総合判定: {'フィードバックページ' if has_any_feedback else '不明なページ形式'}")
                
            elif post_response.status_code == 400:
                print(f"  [CONFIRMED] POST 400エラー - CSRF問題の可能性")
                response_data["html_analysis"]["likely_csrf_error"] = True
            
            else:
                print(f"  [ERROR] 予期しないステータス: {post_response.status_code}")
        
        except Exception as e:
            print(f"  [EXCEPTION] {str(e)}")
            response_data["error"] = str(e)
        
        return response_data
    
    def run_comprehensive_html_analysis(self):
        """
        Run comprehensive HTML analysis for all failing question types
        """
        print("Enhanced HTML Response Analysis - Deep Production Investigation")
        print("Beyond Surface Level Testing - Comprehensive HTML Analysis")
        print("=" * 70)
        
        test_scenarios = [
            {"name": "basic_questions", "dept": "basic", "type": "basic"},
            {"name": "civil_planning_specialist", "dept": "civil_planning", "type": "specialist"},
            {"name": "road_specialist_reference", "dept": "road", "type": "specialist"}
        ]
        
        for scenario in test_scenarios:
            response_data = self.capture_detailed_response(
                scenario["dept"], scenario["type"], scenario["name"]
            )
            self.analysis_results["question_type_responses"][scenario["name"]] = response_data
            
            # Brief delay between tests
            time.sleep(2)
        
        # Comparative Analysis
        self.perform_comparative_analysis()
        
        # Save results
        self.save_analysis_results()
        
        return self.analysis_results
    
    def perform_comparative_analysis(self):
        """
        Compare responses between working and failing question types
        """
        print(f"\n" + "=" * 70)
        print("Comparative Analysis: Working vs Failing Question Types")
        print("=" * 70)
        
        responses = self.analysis_results["question_type_responses"]
        
        # Compare feedback detection methods
        comparison = {}
        
        for test_name, response_data in responses.items():
            if "html_analysis" in response_data:
                html_analysis = response_data["html_analysis"]
                comparison[test_name] = {
                    "post_status": response_data.get("post_response", {}).get("status_code"),
                    "feedback_detected": html_analysis.get("feedback_detected", False),
                    "next_link_present": html_analysis.get("next_link_present", False),
                    "page_title": html_analysis.get("page_title", ""),
                    "feedback_indicators_count": sum(1 for v in html_analysis.get("feedback_indicators", {}).values() if v),
                    "error_indicators_count": sum(1 for v in html_analysis.get("error_indicators", {}).values() if v)
                }
        
        self.analysis_results["comparative_analysis"] = comparison
        
        print(f"\n比較分析結果:")
        for test_name, analysis in comparison.items():
            print(f"\n  {test_name}:")
            print(f"    POSTステータス: {analysis['post_status']}")
            print(f"    フィードバック検出: {analysis['feedback_detected']}")
            print(f"    次問題リンク: {analysis['next_link_present']}")
            print(f"    ページタイトル: {analysis['page_title']}")
            print(f"    フィードバック指標数: {analysis['feedback_indicators_count']}")
            print(f"    エラー指標数: {analysis['error_indicators_count']}")
        
        # Identify patterns
        working_tests = [name for name, analysis in comparison.items() if analysis['feedback_detected']]
        failing_tests = [name for name, analysis in comparison.items() if not analysis['feedback_detected']]
        
        print(f"\n\n[パターン分析]")
        print(f"正常動作: {working_tests}")
        print(f"異常動作: {failing_tests}")
        
        if failing_tests:
            print(f"\n[根本原因候補]")
            print(f"- フィードバックページのHTML構造が期待される形式と異なる")
            print(f"- 特定の質問タイプで異なるテンプレートが使用されている")
            print(f"- POSTリクエスト処理で問題が発生している")
    
    def save_analysis_results(self):
        """Save detailed analysis results"""
        with open('enhanced_html_response_analysis.json', 'w', encoding='utf-8') as f:
            json.dump(self.analysis_results, f, ensure_ascii=False, indent=2)
        print(f"\n詳細分析結果保存: enhanced_html_response_analysis.json")

if __name__ == "__main__":
    analyzer = EnhancedHTMLResponseAnalyzer()
    results = analyzer.run_comprehensive_html_analysis()