import os
from datetime import datetime
from google import genai
from google.genai import types
import smtplib
from email.message import EmailMessage

# 1. 클라이언트 설정
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

def get_report():
    prompt = """
    당신은 전문 금융 분석가입니다. 
    오늘 날짜 기준, 간밤(전일 종가까지 하루 동안) ICE 거래소의 금(Gold)과 은(Silver) 선물 시장을 분석해 주세요.

    1. **가격 데이터**: 표(Table) 형식을 사용하여 [종가], [전일 대비 변동폭], [변동률(%)]을 작성해 주세요.
    2. **하루 변동 원인 분석**: 전일 하루 동안 발생한 구체적인 경제 지표, 연준 발언, 달러 인덱스 변화를 요약해 주세요.
    3. **톤**: 전문적이고 간결한 한국어로 작성해 주세요.
    """
    
    # 시도해볼 모델 목록 (가장 성공 확률이 높은 순서)
    model_names = ['gemini-2.0-flash', 'models/gemini-1.5-flash', 'gemini-1.5-flash']
    
    for model_name in model_names:
        try:
            response = client.models.generate_content(
                model=model_name, 
                contents=prompt,
                config=types.GenerateContentConfig(
                    tools=[types.Tool(google_search=types.GoogleSearch())]
                )
            )
            return response.text
        except Exception as e:
            if "404" in str(e):
                continue # 다음 모델로 재시도
            return f"리포트 생성 중 오류 발생 ({model_name}): {str(e)}"
    
    return "제공된 모든 모델 이름을 시도했으나 찾을 수 없습니다. API 키 설정을 확인해 주세요."

def send_email(content):
    msg = EmailMessage()
    msg["Subject"] = f"📊 [ICE 시황] 금/은 일일 리포트 ({datetime.now().strftime('%Y-%m-%d')})"
    msg["From"] = os.environ["EMAIL_USER"]
    msg["To"] = os.environ["EMAIL_RECEIVER"]
    msg.set_content(content)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(os.environ["EMAIL_USER"], os.environ["EMAIL_PASS"])
        smtp.send_message(msg)

if __name__ == "__main__":
    report_content = get_report()
    send_email(report_content)
    print("Execution Finished.")
