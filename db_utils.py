#db관련 코드
from pymongo import MongoClient

# MongoDB 연결 설정
def get_db():
    client = MongoClient('mongodb://localhost:27017/')
    db = client['job_portal']
    return db

# 데이터 저장 함수
def save_job_data(job_data):
    db = get_db()
    jobs_collection = db['jobs']

    # 중복 확인 (URL 기준)
    existing_job = jobs_collection.find_one({'url': job_data['url']})
    if not existing_job:
        jobs_collection.insert_one(job_data)
        print(f"Saved: {job_data['title']}")
    else:
        print(f"Duplicate found: {job_data['title']}")
