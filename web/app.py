import streamlit as st
from sqlalchemy import create_engine, Table, Column, Integer, String, DateTime, MetaData, select
from datetime import datetime
import pandas as pd
import os

# Настройки подключения к базе
DB_USER = os.getenv('POSTGRES_USER', 'user')
DB_PASS = os.getenv('POSTGRES_PASSWORD', 'password')
DB_HOST = os.getenv('DB_HOST', 'db')
DB_NAME = os.getenv('POSTGRES_DB', 'todo_db')

database_url = f'postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:5432/{DB_NAME}'
engine = create_engine(database_url)
metadata = MetaData()

todos = Table(
    'todos', metadata,
    Column('id', Integer, primary_key=True),
    Column('title', String(255), nullable=False),
    Column('created_at', DateTime, default=datetime.utcnow),
    Column('completed_at', DateTime, nullable=True)
)

# Главная страница
st.title("Список дел")

# Форма добавления нового дела
with st.form("add_todo", clear_on_submit=True):
    new_title = st.text_input("Название дела")
    submitted = st.form_submit_button("Добавить")
    if submitted and new_title:
        with engine.begin() as conn:
            conn.execute(todos.insert().values(title=new_title))
        st.success("Дело добавлено")

# Загрузка текущих дел из БД
with engine.connect() as conn:
    result = conn.execute(select(todos)).fetchall()

# Отображение таблицы дел
if result:
    df = pd.DataFrame(result, columns=['id', 'title', 'created_at', 'completed_at'])
    st.dataframe(df)

    # Форма удаления
    with st.form("delete_todo"):
        del_id = st.number_input("ID для удаления", min_value=1, step=1)
        del_sub = st.form_submit_button("Удалить")
        if del_sub:
            with engine.begin() as conn:
                conn.execute(todos.delete().where(todos.c.id == del_id))
            st.success(f"Дело {del_id} удалено")
else:
    st.info("Дела не найдены")