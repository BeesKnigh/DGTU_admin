import streamlit as st
import requests
import json

api_url = "http://45.155.207.232:1290/api/user"


if 'privileges_prefix' not in st.session_state:
    st.session_state['privileges_prefix'] = ""
if 'name' not in st.session_state:
    st.session_state['name'] = ""
if 'legend' not in st.session_state:
    st.session_state['legend'] = ""
if 'history' not in st.session_state:
    st.session_state['history'] = ""


def login():
    username = st.sidebar.text_input("Имя пользователя", key="login_username")
    password = st.sidebar.text_input("Пароль", type="password", key="login_password")
    if st.sidebar.button('Войти'):
        if not username or not password:
            st.warning("Пожалуйста, введите имя пользователя и пароль.")
        else:
            response = requests.get(f"{api_url}/login", params={"username": username, "password": password})
            if response.status_code == 200:
                user_data = response.json()
                st.session_state['logged_in'] = True
                st.session_state['username'] = user_data.get('username')
                st.session_state['auth_hash'] = user_data.get('auth_hash')
            else:
                st.error("Ошибка входа")


def register():
    st.subheader("Регистрация")
    new_username = st.text_input("Имя пользователя", key="reg_username")
    new_password = st.text_input("Пароль", type="password", key="reg_password")
    new_name = st.text_input("Имя", key="reg_name")
    new_family = st.text_input("Фамилия", key="reg_family")
    new_two_name = st.text_input("Отчество", key="reg_two_name")
    if st.button("Зарегистрироваться"):
        if not new_username or not new_password or not new_name or not new_family or not new_two_name:
            st.warning("Пожалуйста, заполните все поля.")
        else:
            response = requests.post(
                f"{api_url}/register",
                params={
                    "username": new_username,
                    "password": new_password,
                    "name": new_name,
                    "family": new_family,
                    "two_name": new_two_name,
                },
            )
            if response.status_code == 200:
                st.success("Регистрация прошла успешно! Пожалуйста, войдите.")
                login()
            else:
                st.error("Ошибка регистрации")


def dashboard():
    username = st.session_state.get('username')
    if username:
        st.write(f"Имя пользователя: {username}")
    else:
        st.write("Имя пользователя не найдено.")
    st.write(f"Токен авторизации: {st.session_state.get('auth_hash')}")


def manage_roles():
    st.subheader("Управление ролями")

    if st.button("Добавить роль"):
        user_id = st.number_input("ID пользователя", min_value=1)
        privileges_prefix = st.text_input("Префикс привилегий")
        if st.button("Подтвердить"):
            response = requests.get(
                f"{api_url}/privileges/set",
                params={
                    "user_id": user_id,
                    "privileges_prefix": privileges_prefix
                }
            )
            if response.status_code == 200:
                st.success("Роль успешно добавлена!")
            else:
                st.error("Ошибка при добавлении роли.")

    if st.button("Узнать роль"):
        st.warning("Функциональность 'Узнать роль' пока не реализована.")

    if st.button("Узнать все роли"):
        response = requests.get(f"{api_url}/privileges/all")
        if response.status_code == 200:
            roles_data = response.json()
            with st.expander("Список ролей"):
                for role in roles_data:
                    st.write(f"**Префикс:** {role['privileges_prefix']}")
                    st.write(f"**Название:** {role['name']}")
                    st.write(f"**Описание:** {role['legend']}")
                    st.write(f"**Условия получения:** {role['history']}")
                    st.write("---")
        else:
            st.error("Ошибка при получении списка ролей.")
    if st.button("Создать новую роль"):
        privileges_prefix = st.text_input("Префикс привилегий", key="privileges_prefix", value=st.session_state['privileges_prefix'])
        name = st.text_input("Название роли", key="name", value=st.session_state['name'])
        legend = st.text_input("Описание", key="legend", value=st.session_state['legend'])
        history = st.text_input("Условия получения", key="history", value=st.session_state['history'])

        if st.button("Подтвердить создание"):
            st.session_state['privileges_prefix'] = privileges_prefix
            st.session_state['name'] = name
            st.session_state['legend'] = legend
            st.session_state['history'] = history

            new_role_data = {
                "privileges_prefix": privileges_prefix,
                "name": name,
                "legend": legend,
                "history": history
            }

            response = requests.post(
                f"{api_url}/privileges/new",
                data=json.dumps(new_role_data),
                headers={'Content-Type': 'application/json'}
            )

            if response.status_code == 200:
                st.success("Новая роль создана!")
            else:
                st.error("Ошибка при создании новой роли.")


def main():
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    if not st.session_state['logged_in']:
        st.sidebar.title("Аутентификация")
        page = st.sidebar.selectbox("Выберите действие", ["Войти", "Зарегистрироваться"])
        if page == "Войти":
            login()
        elif page == "Зарегистрироваться":
            register()
    else:
        st.sidebar.title("Личный кабинет")
        dashboard_option = st.sidebar.selectbox(
            "Выберите действие",
            ["Посмотреть все карты", "Создать карту", "Удаление карт", "Посмотреть всех пользователей", "Управление ролями"]
        )
        if dashboard_option == "Посмотреть все карты":
            pass
        elif dashboard_option == "Посмотреть всех пользователей":
            response = requests.get(f"{api_url}")
            if response.status_code == 200:
                users_data = response.json()
                for user in users_data:
                    st.write(f"ID: {user['user_id']}, Username: {user['username']}")
            else:
                st.error("Ошибка при получении списка пользователей.")
        elif dashboard_option == "Создать карту":
            pass
        elif dashboard_option == "Удаление карт":
            pass
        elif dashboard_option == "Управление ролями":
            manage_roles()


if __name__ == "__main__":
    main()