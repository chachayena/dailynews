import requests
import smtplib
from email.mime.text import MIMEText
from config import EMAIL, APP_PASSWORD, NEWS_API_KEY, RECIPIENTS

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

#  메일 내용 만들기
def make_summary(us_news, kr_news):
    summary = "오늘의 경제 뉴스\n\n"

    summary += "🇺🇸 미국 뉴스\n"
    for i, news in enumerate(us_news, 1):
        summary += f"{i}. {news['title']}\n{news['url']}\n\n"

    summary += "🇰🇷 한국 뉴스\n"
    for i, news in enumerate(kr_news, 1):
        summary += f"{i}. {news['title']}\n{news['url']}\n\n"

    return summary

#  이메일 발송
def send_email(content):
    recipients = RECIPIENTS.split(",")

    msg = MIMEText(content)
    msg["Subject"] = "한미 경제 뉴스"
    msg["From"] = EMAIL
    msg["To"] = ", ".join(recipients)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL, APP_PASSWORD)
        server.sendmail(EMAIL, recipients, msg.as_string())

#  실행
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
    
