import requests
import smtplib
from email.mime.text import MIMEText
import os

# 환경변수 불러오기
EMAIL = os.getenv("EMAIL")
APP_PASSWORD = os.getenv("APP_PASSWORD")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
RECIPIENTS = os.getenv("RECIPIENTS")

#print("메일:", os.getenv("EMAIL"))
#print("앱비번:", os.getenv("APP_PASSWORD"))
#print("뉴스키:", os.getenv("NEWS_API_KEY"))
#print("수신자:", os.getenv("RECIPIENTS"))

# 환경변수 체크
for name, val in [("EMAIL", EMAIL), ("APP_PASSWORD", APP_PASSWORD), 
                  ("NEWS_API_KEY", NEWS_API_KEY), ("RECIPIENTS", RECIPIENTS)]:
    if not val:
        raise ValueError(f"{name} 환경변수가 설정되지 않음")

# 안전하게 split 처리
recipients = [r.strip() for r in RECIPIENTS.split(",") if r.strip()]
if not recipients:
    raise ValueError("RECIPIENTS 환경변수가 비어있습니다.")


# 🇺🇸 미국 데일리 뉴스
#def get_us_news():
#    url = f"https://newsapi.org/v2/top-headlines?country=us&category=business&apiKey={NEWS_API_KEY}"
#    res = requests.get(url)
#    data = res.json()
#    return data.get("articles", [])[:5]

# 🇰🇷 한국 뉴스
#def get_kr_news():
#    url = f"https://newsapi.org/v2/top-headlines?country=kr&q=business&apiKey={NEWS_API_KEY}"
#    res = requests.get(url)
#    data = res.json()
#    return data.get("articles", [])[:5]

# 메일 내용 만들기
#def make_summary(us_news, kr_news):
#    summary = "오늘의 부동산 뉴스\n\n"

#    summary += "🇺🇸 미국 뉴스\n"
#    for i, news in enumerate(us_news, 1):
#        summary += f"{i}. {news['title']}\n{news['url']}\n\n"

#    summary += "🇰🇷 한국 뉴스\n"
#    for i, news in enumerate(kr_news, 1):
#        summary += f"{i}. {news['title']}\n{news['url']}\n\n"

#    return summary


# 이메일 발송
#def send_email(content):
#    msg = MIMEText(content)
#    msg["Subject"] = "한미 경제 뉴스"
#    msg["From"] = EMAIL
#    msg["To"] = ", ".join(recipients)

#    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
#        server.login(EMAIL, APP_PASSWORD)
#        server.sendmail(EMAIL, recipients, msg.as_string())

# 실행
#if __name__ == "__main__":
#    us_news = get_us_news()
#    kr_news = get_kr_news()

#    summary = make_summary(us_news, kr_news)



# 지난 7일 날짜 계산
today = datetime.today()
seven_days_ago = today - timedelta(days=7)
from_date = seven_days_ago.strftime("%Y-%m-%d")
to_date = today.strftime("%Y-%m-%d")

# 🇰🇷 한국 부동산 뉴스 (지난 7일)
def get_kr_real_estate_news_week():
    url = (
        f"https://newsapi.org/v2/everything?"
        f"q=부동산&language=ko&from={from_date}&to={to_date}&sortBy=popularity&apiKey={NEWS_API_KEY}"
    )
    res = requests.get(url)
    data = res.json()
    return data.get("articles", [])[:10]  # 상위 10개 기사

# 메일 내용 만들기
def make_summary(kr_news):
    summary = f"한국 부동산 뉴스 요약 ({from_date} ~ {to_date})\n\n"
    for i, news in enumerate(kr_news, 1):
        summary += f"{i}. {news['title']}\n{news['url']}\n\n"
    return summary

# 이메일 발송
def send_email(content):
    msg = MIMEText(content)
    msg["Subject"] = f"한주간 부동산 뉴스 요약 ({from_date} ~ {to_date})"
    msg["From"] = EMAIL
    msg["To"] = ", ".join(recipients)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL, APP_PASSWORD)
        server.sendmail(EMAIL, recipients, msg.as_string())

# 실행
if __name__ == "__main__":
    kr_news = get_kr_real_estate_news_week()
    summary = make_summary(kr_news)



    print("메일 보내기 시작")
    try:
        send_email(summary)
        print("메일 성공")
    except Exception as e:
        print("메일 실패:", e)