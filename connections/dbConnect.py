import ydb
import ydb.iam
import sys

# Укажите свои параметры подключения
ENDPOINT = "grpcs://ydb.serverless.yandexcloud.net:2135"
DATABASE = "/ru-central1/b1gb2ho0vh9cddbcqjt4/etnjkb3gtbtoti2j2su0"   # замените на ваши
KEY_PATH = r"C:/Users/Margo/Downloads/authorized_key.json"  # либо IAM-токен, либо OAuth-токен


def connect():
    # Загружаем креды из JSON
    credentials = ydb.iam.ServiceAccountCredentials.from_file(KEY_PATH)

    # Создаём драйвер
    driver = ydb.Driver(
        endpoint=ENDPOINT,
        database=DATABASE,
        credentials=credentials,
    )

    # Проверяем подключение
    try:
        driver.wait(fail_fast=True, timeout=5)
        print("Успешное подключение к YDB")
    except Exception as e:
        print("Ошибка подключения к YDB:", str(e))
        sys.exit(1)
    pool = ydb.SessionPool(driver)
    # Пул сессий
    return pool


