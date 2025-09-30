from connections import dbConnect

pool = dbConnect.connect()


def loadRcData(session):
    return session.transaction().execute(
        "SELECT name FROM rc order by name ASC;",
        commit_tx=True
    )

def returnRC():
    try:
        result_sets = pool.retry_operation_sync(loadRcData)

        rows = result_sets[0].rows
        if not rows:
            print("⚠️ Таблица users пуста или не найдена")
        else:
            return rows
    except Exception as e:
        print("❌ Ошибка при выполнении запроса:", str(e))
