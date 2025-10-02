from connections import dbConnect

pool = dbConnect.connect()


def loadRcData(session):
    return session.transaction().execute(
        "SELECT name FROM rc order by name ASC;",
        commit_tx=True
    )


def loadRcMlListdata(session, rc_name):
    query = """
        DECLARE $rc_name AS Text;
            SELECT 
                iti.id ID, 
                rc.name RC, 
                iti.open_date OpenDate, 
                w.waybill_number w_number, 
                c.ident_code Cars_Ident_Code, 
                t.ident_code Trailers_Ident_Code,
                iti.status status,
                d.first_name First_name,
                d.middle_name Middle_name, 
                d.last_name Last_name, 
            FROM rc 
            JOIN itinerary AS iti ON rc.id = iti.rc_id
            JOIN waybill AS w ON iti.waybill_id = w.id
            JOIN cars AS c ON w.car_id = c.id
            JOIN trailers AS t ON c.trailer_id = t.id
            JOIN drivers AS d ON w.driver_id = d.id
            WHERE rc.name = $rc_name
        """
    prepared_query = session.prepare(query)

    return session.transaction().execute(
        prepared_query,
        parameters={'$rc_name': rc_name},
        commit_tx=True
    )


def loadRcMlListdataActive(session, rc_name):
    query = """
        DECLARE $rc_name AS Text;
            SELECT 
                iti.id ID, 
                rc.name RC, 
                iti.open_date OpenDate, 
                iti.ml_id ML_ID, 
                c.ident_code Cars_Ident_Code, 
                t.ident_code Trailers_Ident_Code,
                iti.status status,
                d.first_name First_name,
                d.middle_name Middle_name, 
                d.last_name Last_name, 
            FROM rc 
            JOIN itinerary AS iti ON rc.id = iti.rc_id
            JOIN waybill AS w ON iti.waybill_id = w.id
            JOIN cars AS c ON w.car_id = c.id
            JOIN trailers AS t ON c.trailer_id = t.id
            JOIN drivers AS d ON w.driver_id = d.id
            WHERE rc.name = $rc_name and (status = 'открыт' or status = 'завершен')
            order by iti.id ASC, status desc;
        """
    prepared_query = session.prepare(query)

    return session.transaction().execute(
        prepared_query,
        parameters={'$rc_name': rc_name},
        commit_tx=True
    )

def openActiveRoute(session, route_id):
    query = """
            DECLARE $route_id AS Int64;
               
               UPDATE itinerary set
               status = 'открыт'
               where id = $route_id;
            """
    prepared_query = session.prepare(query)

    return session.transaction().execute(
        prepared_query,
        parameters={'$route_id': route_id},
        commit_tx=True
    )

def returnRC():
    try:
        result_sets = pool.retry_operation_sync(loadRcData)

        rows = result_sets[0].rows
        if not rows:
            print("Таблица users пуста или не найдена")
        else:
            return rows
    except Exception as e:
        print("Ошибка при выполнении запроса:", str(e))


def returnMldata(rc_name):
    try:
        result_sets = pool.retry_operation_sync(lambda session: loadRcMlListdata(session, rc_name))
        rows = result_sets[0].rows
        if not rows:
            print("Таблица users пуста или не найдена")
        else:
            return rows
    except Exception as e:
        print("Ошибка при выполнении запроса:", str(e))


def returnMldataActive(rc_name):
    try:
        result_sets = pool.retry_operation_sync(lambda session: loadRcMlListdataActive(session, rc_name))
        rows = result_sets[0].rows
        if not rows:
            print("Таблица users пуста или не найдена")
        else:
            return rows
    except Exception as e:
        print("Ошибка при выполнении запроса:", str(e))


def openRouteWithRouteId(route_id):
    try:
        result_sets = pool.retry_operation_sync(lambda session: openActiveRoute(session, route_id))


        return "Маршрут успешно открыт"
    except Exception as e:
        print("Ошибка при выполнении запроса:", str(e))
