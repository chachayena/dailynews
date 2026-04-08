import os
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from datetime import datetime, timedelta
import pdfkit  # PDF 변환용 (pip install pdfkit)
import tempfile

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

#    print("메일 보내기 시작")
#    try:
#        send_email(summary)
#        print("메일 성공")
#    except Exception as e:
#        print("메일 실패:", e)


# 한국 부동산 뉴스 키워드
KEYWORDS = [
    "부동산", "상가 매매", "아파트 매매", 
    "집값", "전세", "월세", "부동산 정책",
    "부동산 규제", "서울 부동산", "삼성동 개발", "강동구 개발",
    "강남 부동산", "수도권 아파트"]

# 지난 7일 뉴스 날짜 범위
to_date = datetime.today()
from_date = to_date - timedelta(days=7)
to_str = to_date.strftime("%Y-%m-%d")
from_str = from_date.strftime("%Y-%m-%d")

# 한국 부동산 뉴스 가져오기
def filter_real_estate_articles(articles):
    filtered = []
    for article in articles:
        title_text = article.get('title', '').lower()
        content_text = article.get('content', '').lower()
        if any(kw.lower() in title_text for kw in KEYWORDS) or any(kw.lower() in content_text for kw in KEYWORDS):
            filtered.append(article)
    return filtered

def get_kr_real_estate_news():
    query = " OR ".join(KEYWORDS)
    url = (
        f"https://newsapi.org/v2/everything?"
        f"q={query}&"
        f"from={from_str}&"
        f"to={to_str}&"
        f"language=ko&"
        f"sortBy=publishedAt&"
        f"pageSize=50&"
        f"apiKey={NEWS_API_KEY}"
    )
    res = requests.get(url)
    data = res.json()
    articles = data.get("articles", [])
    articles = filter_real_estate_articles(articles)
    return articles[:10]  # 최대 10개


# 뉴스요약
def summarize(text, max_words=50):
    """
    간단 요약 함수: 텍스트를 max_words 단어로 자르고 '...' 추가
    """
    if not text:
        return "내용 없음"
    
    # 한글 기준으로 공백 기준 단어 분리
    words = text.split()
    
    if len(words) <= max_words:
        return text
    
    return ' '.join(words[:max_words]) + '...'


# -----------------------------
# 보고서 생성 (HTML)
# -----------------------------
def make_html_report(news_list, from_date, to_date):
    period = f"{from_date.strftime('%Y-%m-%d')} ~ {to_date.strftime('%Y-%m-%d')}"
    
    html = f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: 'NanumGothic', 'Apple SD Gothic Neo', sans-serif;
                line-height: 1.5;
            }}
            h2 {{ color: #2c3e50; }}
            h3 {{ margin-bottom: 5px; }}
            p {{ margin-top: 0; margin-bottom: 15px; }}
        </style>
    </head>
    <body>
        <h2>한국 부동산 뉴스 요약 ({period})</h2>
    """
    if not news_list:
        html += "<p>이번 기간 동안 한국 부동산 관련 뉴스가 없습니다.</p>"
        html += "</body></html>"
        return html

    for i, article in enumerate(news_list, 1):
        content = summarize(article.get('content', '내용 없음'), max_words=50)
        html += f"""
        <h3>{i}. {article['title']}</h3>
        <p>{content}</p>
        <p><a href="{article['url']}">원문 보기</a></p>
        <hr>
        """

    html += "</body></html>"
    return html

# -----------------------------
# PDF 생성
# -----------------------------
def create_pdf(html_content):
    tmp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdfkit.from_string(html_content, tmp_pdf.name)
    return tmp_pdf.name

# -----------------------------
# 이메일 발송
# -----------------------------
def send_email(html_content, pdf_path):
    msg = MIMEMultipart()
    msg["Subject"] = "한국 부동산 뉴스 보고서"
    msg["From"] = EMAIL
    msg["To"] = ", ".join(recipients)

    # HTML 본문
    msg.attach(MIMEText(html_content, "html"))

    # PDF 첨부
    with open(pdf_path, "rb") as f:
        part = MIMEApplication(f.read(), Name="report.pdf")
        part['Content-Disposition'] = 'attachment; filename="report.pdf"'
        msg.attach(part)

    # SMTP 발송
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL, APP_PASSWORD)
        server.sendmail(EMAIL, recipients, msg.as_string())

# -----------------------------
# 실행
# -----------------------------
if __name__ == "__main__":
    print("뉴스 수집 시작...")
    kr_news = get_kr_real_estate_news()
    
    print("보고서 생성...")
    html_report = make_html_report(kr_news, from_date, to_date)
    pdf_file = create_pdf(html_report)

    print("메일 보내기 시작...")
    try:
        send_email(html_report, pdf_file)
        print("메일 성공!")
    except Exception as e:
        print("메일 실패:", e)