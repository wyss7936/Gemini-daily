import os
import google.generativeai as genai
import smtplib
from email.message import EmailMessage

# 1. Gemini 설정 (GitHub Secrets에서 가져옴)
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

def get_report():
    model = genai.GenerativeModel(
        model_name='gemini-1.5-flash',
        tools=[{ "google_search_retrieval": {} }]
    )
    
    prompt = """
    오늘 날짜 기준, 간밤 ICE 거래소의 Gold와 Silver 선물 종가와 전일 대비 변화율을 알려줘.
    또한, 가격 변동에 영향을 준 주요 뉴스 3가지를 요약해서 한국어로 리포트를 작성해줘.
    양식: 
    - [금 종가/변화율]
    - [은 종가/변화율]
    - [주요 변동 요인 분석]
    """
    response = model.generate_content(prompt)
    return response.text

def send_email(content):
    msg = EmailMessage()
    msg.set_content(content)
    msg["Subject"] = f"📊 금/은 시장 일일 리포트 ({os.environ.get('DATE', 'Today')})"
    msg["From"] = os.environ["EMAIL_USER"]
    msg.set_content(content)
    msg["To"] = os.environ["EMAIL_RECEIVER"]

    # Gmail SMTP 서버 설정
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(os.environ["EMAIL_USER"], os.environ["EMAIL_PASS"])
        smtp.send_message(msg)

if __name__ == "__main__":
    report_content = get_report()
    send_email(report_content)
    print("리포트 발송 완료!")
