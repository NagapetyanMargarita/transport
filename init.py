from documents.documentCreator import generate_document
from documents.ObjectStorage import YandexStaticKeyStorage
import os

def object_storage(file_path):
    # Прямая передача ключей в конструктор
    storage = YandexStaticKeyStorage(
        key_id='YCA...S',
        secret_key='YCM...h',
        bucket_name='trucking-documents'
    )

    # Тестируем подключение
    if storage.test_connection():
        # Просматриваем файлы
        #storage.list_files()

        # Загружаем документ
        storage.upload_docx_file(file_path)

if __name__ == "__main__":
    nomer1 = "123"
    nomer2 = "456"
    gos_ts = "А123ВС77"
    fio = "Иванов Иван Иванович"
    file_path="documents/route_sheet.docx"

    # Генерация документа
    generate_document(nomer1, nomer2, gos_ts, fio, seal_path="documents/seal.jpg",
                      output_file=file_path)

    object_storage(file_path)
    #Удаление файла
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"Файл удален: {file_path}")
    else:
        print(f"Файл не найден: {file_path}")