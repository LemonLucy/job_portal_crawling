import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup
import datetime
from db_utils import save_job_data, save_company_data

def create_retry_session(retries=3, backoff_factor=0.3, status_forcelist=(500, 502, 503, 504)):
    session = requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

# 재시도 세션 생성
session = create_retry_session()

keyword = input("키워드를 입력하세요 (기본값: 'IT') : ") or "IT"
allPage = input("몇 페이지까지 추출하시겠어요? (기본값: 1) : ") or "1"

# 채용 정보 크롤링
for page in range(1, int(allPage) + 1):
    try:
        response = session.get(
            f'https://www.saramin.co.kr/zf_user/search?search_area=main&search_done=y&search_optional_item=n&searchType=search&searchword={keyword}&recruitSort=relation&recruitPageCount=100&page={page}',
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        response.raise_for_status()
        html = BeautifulSoup(response.text, 'html.parser')
        jobs = html.select('div.item_recruit')

        for job in jobs:
            try:
                today = datetime.datetime.now().strftime('%Y-%m-%d')

                title_element = job.select_one('a')
                title = title_element['title'].strip().replace(',', '') if title_element else None

                company_element = job.select_one('div.area_corp > strong > a')
                company_name = company_element.text.strip() if company_element else None

                job_url = 'https://www.saramin.co.kr' + title_element['href'] if title_element else None

                deadline_element = job.select_one('span.date')
                deadline = deadline_element.text.strip() if deadline_element else None

                location = job.select('div.job_condition > span')[0].text.strip() if len(job.select('div.job_condition > span')) > 0 else None
                experience = job.select('div.job_condition > span')[1].text.strip() if len(job.select('div.job_condition > span')) > 1 else None
                requirement = job.select('div.job_condition > span')[2].text.strip() if len(job.select('div.job_condition > span')) > 2 else None
                jobtype = job.select('div.job_condition > span')[3].text.strip() if len(job.select('div.job_condition > span')) > 3 else None

                job_data = {
                    'date': today,
                    'title': title,
                    'company': company_name,
                    'url': job_url,
                    'deadline': deadline,
                    'location': location,
                    'experience': experience,
                    'requirement': requirement,
                    'jobtype': jobtype,
                }
                save_job_data(job_data)

            except Exception as e:
                print(f"Error processing job: {e}")

    except requests.RequestException as e:
        print(f"Error fetching page {page}: {e}")

# 기업 정보 크롤링
for page in range(1, int(allPage) + 1):
    try:
        response = session.get(
            f'https://www.saramin.co.kr/zf_user/search/company?search_area=main&search_done=y&search_optional_item=n&searchType=search&searchword={keyword}&recruitSort=relation&recruitPageCount=100&page={page}',
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        response.raise_for_status()
        html = BeautifulSoup(response.text, 'html.parser')
        companies = html.select('div.item_corp')  # 기업 리스트 선택

        for company in companies:
            try:
                today = datetime.datetime.now().strftime('%Y-%m-%d')

                # 기업명: h2.corp_name
                company_name_element = company.select_one('h2.corp_name > a')
                company_name = company_name_element.text.strip() if company_name_element else "정보 없음"

                # 상세 정보 파싱
                details = company.select('dl > dt')
                values = company.select('dl > dd')
                details_dict = {dt.text.strip(): dd.text.strip() for dt, dd in zip(details, values)}

                establishment_date = details_dict.get("설립일", "정보 없음")
                ceo_name = details_dict.get("대표자명", "정보 없음")
                industry = details_dict.get("업종", "정보 없음")
                address = details_dict.get("기업주소", "정보 없음")

                # 저장할 데이터 구조
                company_data = {
                    'date': today,
                    'company_name': company_name,
                    'establishment_date': establishment_date,
                    'ceo_name': ceo_name,
                    'industry': industry,
                    'address': address,
                }

                # 데이터 확인
                print(company_data)  # 임시 출력으로 데이터 확인
                save_company_data(company_data)  # 데이터 저장

            except Exception as e:
                print(f"Error processing company: {e}")

    except requests.RequestException as e:
        print(f"Error fetching page {page}: {e}")
