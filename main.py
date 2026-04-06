import requests
import smtplib
from email.mime.text import MIMEText
import os
from datetime import datetime, timedelta

# 환경변수 불러오기
EMAIL = os.getenv("EMAIL")
APP_PASSWORD = os.getenv("APP_PASSWORD")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
RECIPIENTS = os.getenv("RECIPIENTS")


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

# 한국 부동산 뉴스 키워드
KEYWORDS = [
    "부동산", "주택시장", "아파트 매매", "오피스텔",
    "집값", "전세", "월세", "부동산 정책",
    "부동산 규제", "재개발", "재건축", "서울 부동산",
    "강남 부동산", "수도권 아파트", "지방 부동산"
]

# 지난 7일 뉴스 날짜 범위
to_date = datetime.today()
from_date = to_date - timedelta(days=7)
to_str = to_date.strftime("%Y-%m-%d")
from_str = from_date.strftime("%Y-%m-%d")

# 한국 부동산 뉴스 가져오기
def get_kr_real_estate_news():
    query = " OR ".join(KEYWORDS)
    url = (
        f"https://newsapi.org/v2/everything?"
        f"q={query}&"
        f"from={from_str}&"
        f"to={to_str}&"
        f"language=ko&"
        f"sortBy=publishedAt&"
        f"apiKey={NEWS_API_KEY}"
    )
    res = requests.get(url)
    data = res.json()
    return data.get("articles", [])[:10]  # 최대 10건 요약

# 메일 내용 만들기
def make_summary(kr_news):
    summary = f"📅 한국 부동산 뉴스 요약 ({from_str} ~ {to_str})\n\n"
    if not kr_news:
        summary += "이번 주 한국 부동산 관련 뉴스가 없습니다.\n"
    else:
        for i, news in enumerate(kr_news, 1):
            summary += f"{i}. {news['title']}\n{news['url']}\n\n"
    return summary

# 이메일 발송
def send_email(content):
    msg = MIMEText(content)
    msg["Subject"] = f"한국 부동산 뉴스 요약 ({from_str}~{to_str})"
    msg["From"] = EMAIL
    msg["To"] = ", ".join(recipients)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL, APP_PASSWORD)
        server.sendmail(EMAIL, recipients, msg.as_string())

# 실행
if __name__ == "__main__":
    kr_news = get_kr_real_estate_news()
    summary = make_summary(kr_news)

    print("메일 보내기 시작")
    try:
        send_email(summary)
        print("메일 성공")
    except Exception as e:
        print("메일 실패:", e)