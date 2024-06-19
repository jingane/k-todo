import streamlit as st
from sqlalchemy import create_engine, Column, Integer, String, Text, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
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

# 기존 admin 계정 삭제
def delete_admin_account():
    admin_user = session.query(User).filter_by(username='admin').first()
    if admin_user:
        session.delete(admin_user)
        session.commit()

delete_admin_account()

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

def register(username, password):
    if session.query(User).filter_by(username=username).first():
        return False
    user = User(username=username, password=password)
    session.add(user)
    session.commit()
    return True

# Streamlit 세션 상태 초기화
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.user = None

# Streamlit 앱
st.title("Schedule Notepad")

# 사용자 인증 및 회원가입
if not st.session_state.authenticated:
    auth_mode = st.radio("Choose an option", ["Login", "Sign Up"])
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if auth_mode == "Login":
        if st.button("Login"):
            if authenticate(username, password):
                st.session_state.authenticated = True
                st.session_state.user = username
                st.experimental_rerun()
            else:
                st.error("Invalid username or password")
    else:
        if st.button("Sign Up"):
            if register(username, password):
                st.success("User registered successfully")
            else:
                st.error("Username already exists")
else:
    # 날짜 설정
    today = datetime.now(pytz.timezone('Europe/Berlin')).date()
    schedule = get_schedule(today)

    # 메모장 UI
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("오늘 외부")
        external_today = st.text_area(" ", schedule.external_today or "", key="external_today", height=300)
        st.subheader("내일 내부")
        internal_tomorrow = st.text_area(" ", schedule.internal_tomorrow or "", key="internal_tomorrow", height=300)
    with col2:
        st.subheader("오늘 내부")
        internal_today = st.text_area(" ", schedule.internal_today or "", key="internal_today", height=300)
        st.subheader("내일 외부")
        external_tomorrow = st.text_area(" ", schedule.external_tomorrow or "", key="external_tomorrow", height=300)

    # 자동 저장
    if internal_today != schedule.internal_today or \
       external_today != schedule.external_today or \
       internal_tomorrow != schedule.internal_tomorrow or \
       external_tomorrow != schedule.external_tomorrow:
        schedule.internal_today = internal_today
        schedule.external_today = external_today
        schedule.internal_tomorrow = internal_tomorrow
        schedule.external_tomorrow = external_tomorrow
        session.commit()
        st.success("Schedule saved")

    if st.button("Logout"):
        st.session_state.authenticated = False
        st.session_state.user = None
        st.experimental_rerun()
