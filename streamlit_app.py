import streamlit as st
from sqlalchemy import create_engine, Column, Integer, String, Text, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import pytz

# 데이터베이스 설정
DATABASE_URL = 'sqlite:///schedule.db'
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()

# 모델 정의
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(150), unique=True, nullable=False)
    password = Column(String(150), nullable=False)

class Schedule(Base):
    __tablename__ = 'schedules'
    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    internal_today = Column(Text, nullable=True)
    external_today = Column(Text, nullable=True)
    internal_tomorrow = Column(Text, nullable=True)
    external_tomorrow = Column(Text, nullable=True)

Base.metadata.create_all(engine)

# 함수 정의
def get_schedule(date):
    schedule = session.query(Schedule).filter_by(date=date).first()
    if not schedule:
        schedule = Schedule(date=date)
        session.add(schedule)
        session.commit()
    return schedule

def authenticate(username, password):
    user = session.query(User).filter_by(username=username).first()
    if user and user.password == password:
        return True
    return False

# Streamlit 앱
st.title("Schedule Notepad")

# 사용자 인증
username = st.text_input("Username")
password = st.text_input("Password", type="password")
if st.button("Login"):
    if authenticate(username, password):
        st.success("Logged in")

        # 날짜 설정
        today = datetime.now(pytz.timezone('Europe/Berlin')).date()
        schedule = get_schedule(today)

        # 메모장 UI
        st.header("1. 오늘 내부")
        schedule.internal_today = st.text_area("internal_today", schedule.internal_today or "")
        st.header("2. 오늘 외부")
        schedule.external_today = st.text_area("external_today", schedule.external_today or "")
        st.header("3. 내일 내부")
        schedule.internal_tomorrow = st.text_area("internal_tomorrow", schedule.internal_tomorrow or "")
        st.header("4. 내일 외부")
        schedule.external_tomorrow = st.text_area("external_tomorrow", schedule.external_tomorrow or "")

        # 데이터베이스에 저장
        if st.button("Save"):
            session.commit()

    else:
        st.error("Invalid username or password")

# 초기 사용자 추가 (테스트 용도)
if st.button("Add default user (admin/admin)"):
    if not session.query(User).filter_by(username='admin').first():
        user = User(username='admin', password='admin')
        session.add(user)
        session.commit()
        st.success("Default user added")
    else:
        st.info("Default user already exists")
