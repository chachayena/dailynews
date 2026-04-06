import requests
import smtplib
from email.mime.text import MIMEText
import os

# 환경변수 불러오기
EMAIL = os.getenv("EMAIL")
APP_PASSWORD = os.getenv("APP_PASSWORD")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
RECIPIENTS = os.getenv("RECIPIENTS")

print("메일:", os.getenv("EMAIL"))
print("앱비번:", os.getenv("APP_PASSWORD"))
print("뉴스키:", os.getenv("NEWS_API_KEY"))
print("수신자:", os.getenv("RECIPIENTS"))

# 환경변수 체크
if not EMAIL:
    raise ValueError("EMAIL 환경변수가 설정되지 않음")
if not APP_PASSWORD:
    raise ValueError("APP_PASSWORD 환경변수가 설정되지 않음")
if not NEWS_API_KEY:
    raise ValueError("NEWS_API_KEY 환경변수가 설정되지 않음")
if not RECIPIENTS:
    raise ValueError("RECIPIENTS 환경변수가 설정되지 않음")

# 안전하게 split 처리
recipients = [r.strip() for r in RECIPIENTS.split(",") if r.strip()]
if not recipients:
    raise ValueError("RECIPIENTS 환경변수가 비어있습니다.")

# 🇺🇸 미국 뉴스
def get_us_news():
    url = f"https://newsapi.org/v2/top-headlines?country=us&category=business&apiKey={NEWS_API_KEY}"
    res = requests.get(url)
    data = res.json()
    return data.get("articles", [])[:5]

# 🇰🇷 한국 뉴스
def get_kr_news():
    url = f"https://newsapi.org/v2/top-headlines?country=kr&category=business&apiKey={NEWS_API_KEY}"
    res = requests.get(url)
    data = res.json()
    return data.get("articles", [])[:5]

# 메일 내용 만들기
def make_summary(us_news, kr_news):
    summary = "오늘의 경제 뉴스\n\n"

    summary += "🇺🇸 미국 뉴스\n"
    for i, news in enumerate(us_news, 1):
        summary += f"{i}. {news['title']}\n{news['url']}\n\n"

    summary += "🇰🇷 한국 뉴스\n"
    for i, news in enumerate(kr_news, 1):
        summary += f"{i}. {news['title']}\n{news['url']}\n\n"

    return summary

# 이메일 발송
def send_email(content):
    msg = MIMEText(content)
    msg["Subject"] = "한미 경제 뉴스"
    msg["From"] = EMAIL
    msg["To"] = ", ".join(recipients)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL, APP_PASSWORD)
        server.sendmail(EMAIL, recipients, msg.as_string())

# 실행
if __name__ == "__main__":
    us_news = get_us_news()
    kr_news = get_kr_news()

    summary = make_summary(us_news, kr_news)

    print("메일 보내기 시작")
    try:
        send_email(summary)
        print("메일 성공")
    except Exception as e:
        print("메일 실패:", e)