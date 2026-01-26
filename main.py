import os
from datetime import datetime
from google import genai
from google.genai import types
import smtplib
from email.message import EmailMessage

# 1. Gemini 설정 (최신 라이브러리 방식)
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

def get_report():
    # 최신 모델명 및 검색 도구 설정
    prompt = """
    오늘 날짜 기준, 간밤 ICE 거래소의 Gold와 Silver 선물 종가와 전일 대비 변화율을 알려줘.
    또한, 가격 변동에 영향을 준 주요 뉴스 3가지를 요약해서 한국어로 리포트를 작성해줘.
    양식: 
    - [금 종가/변화율]
    - [은 종가/변화율]
    - [주요 변동 요인 분석]
    """
    
    response = client.models.generate_content(
        model='gemini-2.0-flash', # 최신 모델로 업그레이드
        contents=prompt,
        config=types.GenerateContentConfig(
            tools=[types.Tool(google_search=types.GoogleSearch())]
        )
    )
    return response.text

def send_email(content):
    msg = EmailMessage()
    msg["Subject"] = f"📊 금/은 시장 일일 리포트 ({datetime.now().strftime('%Y-%m-%d')})"
    msg["From"] = os.environ["EMAIL_USER"]
    msg["To"] = os.environ["EMAIL_RECEIVER"]
    msg.set_content(content)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(os.environ["EMAIL_USER"], os.environ["EMAIL_PASS"])
        smtp.send_message(msg)

if __name__ == "__main__":
    try:
        report_content = get_report()
        send_email(report_content)
        print("리포트 발송 완료!")
    except Exception as e:
        print(f"오류 발생: {e}")
