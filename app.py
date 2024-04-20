import streamlit as st
import requests
import json

api_url = "http://45.155.207.232:1290/api/user"


def initialize_session_state():
    if 'admin_privileges_prefix' not in st.session_state:
        st.session_state['admin_privileges_prefix'] = ""
    if 'role_name' not in st.session_state:
        st.session_state['role_name'] = ""
    if 'role_description' not in st.session_state:
        st.session_state['role_description'] = ""
    if 'role_requirements' not in st.session_state:
        st.session_state['role_requirements'] = ""
    if 'add_role_user_id' not in st.session_state:
        st.session_state['add_role_user_id'] = 1
    if 'add_role_prefix' not in st.session_state:
        st.session_state['add_role_prefix'] = ""


def login():
    username = st.sidebar.text_input("Имя пользователя", key="login_username")
    password = st.sidebar.text_input("Пароль", type="password", key="login_password")
    if st.sidebar.button('Войти'):
        if not username or not password:
            st.warning("Пожалуйста, введите имя пользователя и пароль.")
        else:
            response = requests.get(
                f"{api_url}/admin/login",
                params={"username": username, "password": password}
            )
            if response.status_code == 200:
                user_data = response.json()
                st.session_state['logged_in'] = True
                st.session_state['username'] = user_data.get('username')
                st.session_state['auth_hash'] = user_data.get('auth_hash')
            else:
                st.error("Ошибка входа")


def register():
    st.subheader("Регистрация нового админа")
    new_username = st.text_input("Имя пользователя", key="reg_username")
    new_password = st.text_input("Пароль", type="password", key="reg_password")
    if st.button("Зарегистрироваться"):
        if not new_username or not new_password:
            st.warning("Пожалуйста, заполните все поля.")
        else:
            response = requests.post(
                f"{api_url}/admin",
                params={
                    "username": new_username,
                    "password": new_password,
                },
            )
            if response.status_code == 200:
                st.success("Регистрация прошла успешно!")
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
    with st.form("add_role_form"):
        user_id = st.number_input("ID пользователя", min_value=1, key="add_role_user_id")
        privileges_prefix = st.text_input("Префикс привилегий", key="add_role_prefix")
        submitted = st.form_submit_button("Подтвердить добавление")
        if submitted:
            auth_token = st.session_state.get('auth_hash')
            if auth_token:
                response = requests.post(
                    f"{api_url}/privileges/set",
                    params={
                        "user_id": user_id,
                        "privileges_prefix": privileges_prefix,
                        "auth_admin": auth_token
                    }
                )
                if response.status_code == 200:
                    st.success("Роль успешно добавлена!")
                else:
                    st.error("Ошибка при добавлении роли.")
            else:
                st.error("Ошибка: токен аутентификации не найден.")
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

    def update_privileges_prefix():
        st.session_state['admin_privileges_prefix'] = st.session_state['create_role_form_privileges_prefix']
        st.session_state['role_name'] = st.session_state['create_role_form_name']
        st.session_state['role_description'] = st.session_state['create_role_form_description']
        st.session_state['role_requirements'] = st.session_state['create_role_form_requirements']
        new_role_data = {
            "privileges_prefix": st.session_state['admin_privileges_prefix'],
            "name": st.session_state['role_name'],
            "legend": st.session_state['role_description'],
            "history": st.session_state['role_requirements']
        }
        auth_token = st.session_state.get('auth_hash')
        if auth_token:
            response = requests.post(
                "http://45.155.207.232:1290/api/user/privileges/new",
                params={"auth_admin": auth_token},
                data=json.dumps(new_role_data),
                headers={'Content-Type': 'application/json'}
            )
            if response.status_code == 200:
                st.success("Новая роль создана!")
            else:
                st.error("Ошибка при создании новой роли.")
        else:
            st.error("Ошибка: токен аутентификации не найден.")

    with st.form("create_role_form"):
        privileges_prefix = st.text_input("Префикс привилегий", key="create_role_form_privileges_prefix",
                                         value=st.session_state['admin_privileges_prefix'])
        name = st.text_input("Название роли", key="create_role_form_name", value=st.session_state['role_name'])
        legend = st.text_input("Описание", key="create_role_form_description",
                               value=st.session_state['role_description'])
        history = st.text_input("Условия получения", key="create_role_form_requirements",
                                value=st.session_state['role_requirements'])
        submitted = st.form_submit_button("Подтвердить создание", on_click=update_privileges_prefix)


def view_all_cards():
    user_id = st.number_input("ID пользователя", min_value=1)
    if st.button("Показать карты"):
        auth_token = st.session_state.get('auth_hash')
        if auth_token:
            response = requests.get(
                f"{api_url}/card/id",
                params={"user_id": user_id, "auth_admin": auth_token},
            )
            if response.status_code == 200:
                cards_data = response.json()
                if 'result' in cards_data:
                    if isinstance(cards_data['result'], list):
                        with st.expander("Список карт"):
                            for card in cards_data['result']:
                                st.write(f"ID пользователя: {card['id']}")
                                st.write(f"Секретный ключ: {card['key']}")
                                st.write("---")
                    else:
                        st.error(f"Ошибка: {cards_data['result']}")
                else:
                    st.error("Неожиданная структура данных в ответе API.")
            else:
                st.error("Ошибка при получении списка карт.")
        else:
            st.error("Ошибка: токен аутентификации не найден.")


def replenish_card():
    st.subheader("Пополнение карты")
    card_hash = st.text_input("Хэш карты")
    price = st.number_input("Сумма пополнения", min_value=0)
    inn = st.number_input("ИНН", min_value=0)

    if st.button("Пополнить"):
        auth_token = st.session_state.get('auth_hash')
        if auth_token:
            data = {
                "card_hash": card_hash,
                "price": price,
                "inn": inn
            }
            response = requests.post(
                f"{api_url}/cash/plus?auth_admin={auth_token}",
                data=json.dumps(data),
                headers={'Content-Type': 'application/json'}
            )
            if response.status_code == 200:
                st.success("Карта успешно пополнена!")
            else:
                st.error("Ошибка при пополнении карты.")
        else:
            st.error("Ошибка: токен аутентификации не найден.")


def user_login():
    username = st.text_input("Имя пользователя (Логин)", key="user_login_username")
    password = st.text_input("Пароль", type="password", key="user_login_password")
    if st.button("Войти как пользователь"):
        if not username or not password:
            st.warning("Пожалуйста, введите имя пользователя и пароль.")
        else:
            response = requests.get(
                f"{api_url}/login",
                params={"username": username, "password": password}
            )
            if response.status_code == 200:
                user_data = response.json()
                st.session_state['logged_in'] = True
                st.session_state['auth_hash'] = user_data.get('auth_hash')
                st.empty()
                user_info_page()
            else:
                st.error("анлак")


def user_registration():
    st.subheader("Регистрация пользователя")
    username = st.text_input("Имя пользователя", key="user_reg_username")
    password = st.text_input("Пароль", type="password", key="user_reg_password")
    name = st.text_input("Имя", key="user_reg_name")
    family = st.text_input("Фамилия", key="user_reg_family")
    two_name = st.text_input("Отчество", key="user_reg_two_name")
    if st.button("Зарегистрироваться"):
        if not username or not password or not name or not family or not two_name:
            st.warning("Пожалуйста, заполните все поля.")
        else:
            response = requests.get(
                f"{api_url}/register",
                params={
                    "username": username,
                    "password": password,
                    "name": name,
                    "family": family,
                    "two_name": two_name
                }
            )
            if response.status_code == 200:
                st.success("Регистрация прошла успешно!")
            else:
                st.error("Ошибка регистрации")

def user_info_page():
    st.title("Информация о пользователе")
    auth_token = st.session_state.get('auth_hash')
    if auth_token:
        response = requests.get(f"{api_url}/me?auth_token={auth_token}")
        if response.status_code == 200:
            user_data = response.json()
            if 'result' in user_data:
                result = user_data['result']
                st.write(f"Имя пользователя: {result['username']}")
                st.write(f"Имя: {result['name']}")
                st.write(f"Фамилия: {result['family']}")
                st.write(f"Отчество: {result['two_name']}")
                st.write(f"Баланс: {result['cash']}")
            else:
                st.error("Неожиданная структура данных в ответе API.")
        else:
            st.error("Ошибка при получении информации о пользователе.")
    else:
        st.error("Ошибка: токен аутентификации не найден.")

def view_all_locations():
    st.subheader("Список всех локаций")
    response = requests.get(f"{api_url}/category/all")
    if response.status_code == 200:
        locations_data = response.json()
        with st.expander("Локации"):
            for location in locations_data:
                st.write(f"ID: {location['id']}, Название: {location['name']}")
    else:
        st.error("Ошибка при получении списка локаций.")

def create_location():
    st.subheader("Создание новой локации")
    with st.form("create_location_form"):
        name = st.text_input("Название локации")
        picture = st.text_input("URL картинки")
        submitted = st.form_submit_button("Создать локацию")
        if submitted:
            auth_token = st.session_state.get('auth_hash')
            if auth_token:
                data = {
                    "name": name,
                    "picture": picture
                }
                response = requests.post(
                    f"{api_url}/category/new?admin_auth={auth_token}",
                    data=json.dumps(data),
                    headers={'Content-Type': 'application/json'}
                )
                if response.status_code == 200:
                    st.success("Локация успешно создана!")
                else:
                    st.error("Ошибка при создании локации.")
            else:
                st.error("Ошибка: токен аутентификации не найден.")


def main():
    initialize_session_state()

    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
    if 'is_admin' not in st.session_state:
        st.session_state['is_admin'] = False

    if st.checkbox("Админ режим", key="admin_mode"):
        st.session_state['is_admin'] = True
        if not st.session_state['logged_in']:
            st.sidebar.title("Аутентификация (админ)")
            login()
        else:
            st.sidebar.title("Админ-панель")
            admin_option = st.sidebar.selectbox(
                "Выберите действие",
                [
                    "Посмотреть все карты",
                    "Создать карту",
                    "Пополнить карту",
                    "Удаление карт",
                    "Посмотреть всех пользователей",
                    "Управление ролями",
                    "Регистрация нового админа",
                    "Управление локациями",
                ]
            )
            if admin_option == "Посмотреть все карты":
                view_all_cards()
            elif admin_option == "Посмотреть всех пользователей":
                if st.button("Показать пользователей"):
                    auth_token = st.session_state.get('auth_hash')
                    if auth_token:
                        response = requests.get(f"{api_url}", params={"auth_admin": auth_token})
                        if response.status_code == 200:
                            users_data = response.json()
                            for user in users_data:
                                st.write(f"ID: {user['user_id']}, Username: {user['username']}")
                        else:
                            st.error("Ошибка при получении списка пользователей.")
                    else:
                        st.error("Ошибка: токен аутентификации не найден.")
            elif admin_option == "Создать карту":
                with st.form("create_card_form"):
                    user_id = st.number_input("ID пользователя", min_value=1, key="create_card_user_id")
                    submitted = st.form_submit_button("Создать карту")
                    if submitted:
                        response = requests.post(
                            f"{api_url}/card",
                            params={"user_id": user_id},
                        )
                        if response.status_code == 200:
                            st.success("Карта успешно создана!")
                            card_data = response.json()
                            st.write(f"Секретный ключ карты: {card_data.get('secret_key')}")
                        else:
                            st.error("Ошибка при создании карты.")
            elif admin_option == "Удаление карт":
                st.warning("Функциональность 'Удаление карт' пока не реализована.")
            elif admin_option == "Управление ролями":
                manage_roles()
            elif admin_option == "Регистрация нового админа":
                register()
            elif admin_option == "Пополнить карту":
                replenish_card()
            elif admin_option == "Управление локациями":
                location_action = st.selectbox(
                    "Выберите действие с локациями",
                    ["Посмотреть все локации", "Создать локацию"]
                )
                if location_action == "Посмотреть все локации":
                    view_all_locations()
                elif location_action == "Создать локацию":
                    create_location()
    else:
        st.session_state['is_admin'] = False
        st.title('Сервис Карта жителя')
        if 'show_registration' not in st.session_state:
            st.session_state['show_registration'] = False
        if not st.session_state['show_registration']:
            user_login()
            if st.button("Нет аккаунта? Зарегистрируйтесь"):
                st.session_state['show_registration'] = True
        else:
            user_registration()
            if st.button("Уже есть аккаунт? Войдите"):
                st.session_state['show_registration'] = False

        if st.session_state['logged_in']:
            if st.button("Личный кабинет"):
                user_info_page()

if __name__ == "__main__":
    main()