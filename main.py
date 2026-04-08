import os
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import pdfkit  # PDF 변환용 (pip install pdfkit)
import tempfile
import re

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

# 중복 기사 제거
def remove_duplicates(articles):
    seen = set()
    unique = []

    for article in articles:
        title = article.get('title')
        if title not in seen:
            seen.add(title)
            unique.append(article)

    return unique


# 중요도 선별
def rank_articles(articles):
    ranked = []

    for article in articles:
        text = (article.get('title','') + ' ' + article.get('content','')).lower()
        
        score = sum(1 for kw in KEYWORDS if kw.lower() in text)

        ranked.append((score, article))

    # 점수 높은 순 정렬
    ranked.sort(key=lambda x: x[0], reverse=True)

    # article만 추출
    return [a[1] for a in ranked]


# 뉴스 본문 가져오기
def get_full_article(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        res = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(res.text, 'html.parser')

        paragraphs = soup.find_all('p')
        text = ' '.join(p.get_text() for p in paragraphs)

        # 너무 짧으면 실패로 간주
        if len(text) < 200:
            return ""

        return text
    except:
        return ""

# 뉴스요약
def summarize(text, max_sentences=2):
    if not text:
        return "내용 없음"

    text = re.sub(r'\s+', ' ', text)
    sentences = re.split(r'[.!?]', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 20]

    if not sentences:
        return "요약할 내용 없음"

    return '. '.join(sentences[:max_sentences]) + '.'


# -----------------------------
# 시장 판단
# -----------------------------

# 키워드 정의
UP_KEYWORDS = ["오름", "상승", "급등", "강세", "매수"]
DOWN_KEYWORDS = ["하락", "약세", "급락", "조정", "매도"]

def market_sentiment(article):
    """
    기사 제목 + 내용에서 키워드 기반으로 상승/하락/중립 판단
    """
    text = (article.get('title','') + ' ' + article.get('content','')).lower()
    up = sum(1 for kw in UP_KEYWORDS if kw.lower() in text)
    down = sum(1 for kw in DOWN_KEYWORDS if kw.lower() in text)
    
    if up > down:
        return "상승세 가능"
    elif down > up:
        return "조정/하락 가능"
    else:
        return "중립"
    
# -----------------------------
# 투자 코멘트 생성
# -----------------------------
def investment_comment(article):
    sentiment = market_sentiment(article)
    title = article.get('title', '')
    return f"<b>시장 판단 / 투자 코멘트:</b> {sentiment}"


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
                font-family: Arial, 'Apple SD Gothic Neo', 'Malgun Gothic', sans-serif;
                background-color: #f4f6f8;
                padding: 30px;
            }}
            .container {{
                max-width: 800px;
                margin: auto;
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            h1 {{
                text-align: center;
                color: #2c3e50;
            }}
            .period {{
                text-align: center;
                color: gray;
                margin-bottom: 30px;
            }}
            .news {{
                margin-bottom: 25px;
            }}
            .news-title {{
                font-size: 18px;
                font-weight: bold;
                color: #34495e;
            }}
            .news-content {{
                margin-top: 8px;
                color: #555;
            }}
            .news-comment {{
                margin-top: 8px;
                color: #e67e22;
                font-style: italic;
            }}
            .link {{
                margin-top: 5px;
                font-size: 13px;
            }}
            hr {{
                border: none;
                border-top: 1px solid #eee;
                margin: 20px 0;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>한국 부동산 뉴스 리포트</h1>
            <div class="period">{period}</div>
    """

    if not news_list:
        html += "<p>이번 기간 동안 뉴스가 없습니다.</p></div></body></html>"
        return html

    for i, article in enumerate(news_list, 1):
        full_text = get_full_article(article['url'])
        content_source = full_text if full_text else article.get('description', '')
        content = summarize(content_source, max_sentences=2)
    
        comment_html = investment_comment(article)

        html += f"""
        <div class="news">
            <div class="news-title">{i}. {article['title']}</div>
            <div class="news-content">{content}</div>
            <div class="news-comment">{comment_html}</div>
            <div class="link"><a href="{article['url']}">기사 원문 보기 →</a></div>
        </div>
        <hr>
        """

CSS도 조금 추가하면 PDF에서 보기 좋

    html += "</div></body></html>"
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

    print("중복 뉴스 제거...")
    kr_news = remove_duplicates(kr_news)

    print("중요 뉴스 정렬...")
    kr_news = rank_articles(kr_news)[:5]
    
    print("보고서 생성...")
    html_report = make_html_report(kr_news, from_date, to_date)
    pdf_file = create_pdf(html_report)

    print("메일 보내기 시작...")
    try:
        send_email(html_report, pdf_file)
        print("메일 성공!")
    except Exception as e:
        print("메일 실패:", e)