import requests
from bs4 import BeautifulSoup
import datetime
from db_utils import save_job_data

keyword = input("키워드를 입력하세요 (기본값: 'IT') : ") or "IT"
allPage = input("몇 페이지까지 추출하시겠어요? (기본값: 1) : ") or "1"

for page in range(1, int(allPage)+1):
    soup = requests.get('https://www.saramin.co.kr/zf_user/search?search_area=main&search_done=y&search_optional_item=n&searchType=search&searchword={}&recruitSort=relation&recruitPageCount=100'.format(keyword, page), headers={'User-Agent': 'Mozilla/5.0'})
    html=BeautifulSoup(soup.text, 'html.parser')
    jobs=html.select('div.item_recruit')

    for job in jobs:
        try:
            today=datetime.datetime.now().strftime('%Y-%m-%d')
            title=job.select_one('a')['title'].strip().replace(',','')
            company=job.select_one('div.area_corp > strong >a').text.strip()
            url='https://www.saramin.co.kr' + job.select_one('a')['href']
            deadline=job.select_one('span.date').text.strip()
            location=job.select('div.job_condition > span')[0].text.strip()
            experience=job.select('div.job_condition > span')[1].text.strip()
            requirement=job.select('div.job_condition > span')[2].text.strip()
            jobtype=job.select('div.job_condition > span')[3].text.strip()

            # 크롤링한 데이터를 사전 형태로 정리
            job_data = {
                'date': today,
                'title': title,
                'company': company,
                'url': url,
                'deadline': deadline,
                'location': location,
                'experience': experience,
                'requirement': requirement,
                'jobtype': jobtype,
            }

            # 데이터 저장 호출
            save_job_data(job_data)

            print(today, title,company,url, deadline,location,experience,jobtype)

        except Exception as e:
            print(f"Error processing job: {e}")