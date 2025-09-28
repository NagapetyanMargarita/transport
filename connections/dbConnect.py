import ydb
import ydb.iam
import sys

# Укажите свои параметры подключения
ENDPOINT = "grpcs://ydb.serverless.yandexcloud.net:2135"
DATABASE = "/ru-central1/b1gb2ho0vh9cddbcqjt4/etnjkb3gtbtoti2j2su0"   # замените на ваши
KEY_PATH = r"../authorized_key.json"  # либо IAM-токен, либо OAuth-токен


def connect_and_query():
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
        print("✅ Успешное подключение к YDB")
    except Exception as e:
        print("❌ Ошибка подключения к YDB:", str(e))
        sys.exit(1)

    # Пул сессий
    pool = ydb.SessionPool(driver)

    # Запрос
    def select_all_users(session):
        return session.transaction().execute(
            "SELECT * FROM users;",
            commit_tx=True
        )

    try:
        result_sets = pool.retry_operation_sync(select_all_users)

        rows = result_sets[0].rows
        if not rows:
            print("⚠️ Таблица users пуста или не найдена")
        else:
            for row in rows:
                print(dict(row))  # превращаем строку в словарь
    except Exception as e:
        print("❌ Ошибка при выполнении запроса:", str(e))
    finally:
        driver.stop()


if __name__ == "__main__":
    connect_and_query()
