import os
from datetime import datetime
from google import genai
from google.genai import types
import smtplib
from email.message import EmailMessage

# 1. Gemini 클라이언트 설정
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

def get_report():
    # 전일 하루 동안의 변동 원인과 표 형식을 강조한 프롬프트
    prompt = """
    당신은 전문 금융 분석가입니다. 
    오늘 날짜 기준, 간밤(전일 종가까지 하루 동안) ICE 거래소의 금(Gold)과 은(Silver) 선물 시장을 분석해 주세요.

    1. **가격 데이터**: 표(Table) 형식을 사용하여 [종가], [전일 대비 변동폭], [변동률(%)]을 일목요연하게 작성해 주세요.
    2. **하루 변동 원인 분석**: 장기적 전망은 배제하고, **오직 전일 하루 동안 발생한 구체적인 경제 지표 발표, 연준 위원 발언, 지정학적 사건, 달러 인덱스 변화** 등 실시간 변동 요인을 3가지 이내로 요약해 주세요.
    3. **톤**: 전문적이고 간결한 한국어로 작성해 주세요.
    """
    
    try:
        # 모델명 앞에 'models/'를 붙여 경로를 명확히 지정하여 404 에러를 방지합니다.
        # 무료 티어에서 한도가 넉넉한 1.5-flash 버전을 사용합니다.
        response = client.models.generate_content(
            model='models/gemini-1.5-flash', 
            contents=prompt,
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())]
            )
        )
        return response.text
    except Exception as e:
        # 에러 발생 시 상세 내용을 리턴하여 메일로 확인 가능하게 합니다.
        return f"리포트 생성 중 오류가 발생했습니다: {str(e)}"

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
    # 오류 메시지가 포함되더라도 메일을 발송하여 상태를 확인합니다.
    send_email(report_content)
    print("Execution Finished.")
