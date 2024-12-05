from pymongo import MongoClient
from datetime import datetime, timedelta
import re

# MongoDB 연결 설정
def get_db():
    client = MongoClient('mongodb://113.198.66.75:13122/')
    db = client['job_portal']
    return db

# 채용 공고 데이터 저장
def save_job_data(job_data):
    db = get_db()
    jobs_collection = db['jobs']

    # 중복 확인 (URL 기준)
    existing_job = jobs_collection.find_one({'url': job_data['url']})
    if not existing_job:
        # 데이터 정제 및 저장
        job_data = clean_job_data(job_data)
        if job_data:
            jobs_collection.insert_one(job_data)
            print(f"Saved job: {job_data['title']}")
        else:
            print(f"Invalid job data skipped for URL: {job_data['url']}")
    else:
        print(f"Duplicate job found: {job_data['title']}")

# 채용 공고 데이터 정제
def clean_job_data(job_data):
    required_fields = ['date', 'title', 'company', 'url', 'deadline']
    if not all(field in job_data and job_data[field] for field in required_fields):
        return None

    for key in job_data:
        if isinstance(job_data[key], str):
            job_data[key] = job_data[key].strip()

    job_data['date'] = parse_date(job_data['date'])
    job_data['deadline'], job_data['deadline_type'] = parse_deadline(job_data['deadline'])

    return job_data

# 날짜 변환
def parse_date(date_str):
    try:
        return datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        print(f"Invalid date format: {date_str}")
        return None

# 마감일 변환
def parse_deadline(deadline_str):
    try:
        match = re.search(r'~ (\d{2})/(\d{2})', deadline_str)
        if match:
            month, day = match.groups()
            year = datetime.now().year
            return datetime(year, int(month), int(day)), "STANDARD"

        match_kr = re.search(r'(\d{1,2})월\s*(\d{1,2})일', deadline_str)
        if match_kr:
            month, day = match_kr.groups()
            year = datetime.now().year
            return datetime(year, int(month), int(day)), "STANDARD"

        if "오늘마감" in deadline_str:
            return datetime.now(), "RELATIVE"

        if "내일마감" in deadline_str:
            return datetime.now() + timedelta(days=1), "RELATIVE"

        if "상시채용" in deadline_str or "채용시" in deadline_str:
            return None, "OPEN_ENDED"
        
        if "진행예정" in deadline_str:
            return None, "SCHEDULED"

        print(f"Unhandled deadline format: {deadline_str}")
        return None, "UNKNOWN"
    except Exception as e:
        print(f"Error parsing deadline: {e}")
        return None, "ERROR"

# 기업 정보 데이터 저장
def save_company_data(company_data):
    db = get_db()
    companies_collection = db['companies']

    # 중복 확인 (company_name과 address 기준)
    existing_company = companies_collection.find_one({
        'company_name': company_data['company_name'],
        'address': company_data['address']
    })
    if not existing_company:
        # 데이터 정제 및 저장
        company_data = clean_company_data(company_data)
        if company_data:
            companies_collection.insert_one(company_data)
            print(f"Saved company: {company_data['company_name']}")
        else:
            print(f"Invalid company data skipped: {company_data['company_name']}")
    else:
        print(f"Duplicate company found: {company_data['company_name']}")

# 기업 정보 데이터 정제
def clean_company_data(company_data):
    required_fields = ['date', 'company_name', 'address']
    if not all(field in company_data and company_data[field] for field in required_fields):
        return None

    for key in company_data:
        if isinstance(company_data[key], str):
            company_data[key] = company_data[key].strip()

    company_data['date'] = parse_date(company_data['date'])

    return company_data
