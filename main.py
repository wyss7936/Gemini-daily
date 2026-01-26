import os
from datetime import datetime
from google import genai
from google.genai import types
import smtplib
from email.message import EmailMessage

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

def get_report():
    prompt = "오늘 기준 ICE 거래소의 Gold/Silver 종가, 변화율, 주요 요인을 한국어로 리포트해줘."
    
    response = client.models.generate_content(
        model='gemini-1.5-flash', # 더 안정적인 1.5 버전으로 변경
        contents=prompt,
        config=types.GenerateContentConfig(
            tools=[types.Tool(google_search=types.GoogleSearch())]
        )
    )
    return response.text

def send_email(content):
    msg = EmailMessage()
    msg["Subject"] = f"📊 금/은 시황 리포트 ({datetime.now().strftime('%Y-%m-%d')})"
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
        print("Success!")
    except Exception as e:
        print(f"Error: {e}")
