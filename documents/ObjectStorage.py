import boto3
import os
from datetime import datetime
from botocore.exceptions import ClientError, NoCredentialsError
import requests


class YandexStaticKeyStorage:
    def __init__(self, key_id=None, secret_key=None, bucket_name=None):
        self.key_id = key_id
        self.secret_key = secret_key
        self.bucket_name = bucket_name

        # Создаем клиент для Yandex Object Storage
        self.s3_client = boto3.client(
            's3',
            endpoint_url='https://storage.yandexcloud.net',
            aws_access_key_id=self.key_id,
            aws_secret_access_key=self.secret_key,
            region_name='ru-central1'
        )

    def test_connection(self):
        """Тестирование подключения к Object Storage"""
        try:
            response = self.s3_client.list_buckets()
            buckets = [bucket['Name'] for bucket in response['Buckets']]

            # Проверяем доступ к целевому бакету
            if self.bucket_name in buckets:
                print(f"Подключение успешно. Бакет '{self.bucket_name}' доступен")
            else:
                print(f"Ошибка в подключении. Бакет '{self.bucket_name}' не найден")

            return True

        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'InvalidAccessKeyId':
                print("Ошибка: Неверный key_id")
            elif error_code == 'SignatureDoesNotMatch':
                print("Ошибка: Неверный secret")
            else:
                print(f"Ошибка подключения: {e}")
            return False

    def upload_docx_file(self, file_path, object_key=None, metadata=None):
        try:
            # Проверяем существование файла
            if not os.path.exists(file_path):
                return {
                    'success': False,
                    'error': f'Файл не найден: {file_path}'
                }

            # Генерируем ключ если не указан
            if not object_key:
                filename = os.path.basename(file_path)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                object_key = f"documents/{timestamp}_{filename}"

            # Базовые метаданные
            file_metadata = {
                'uploaded_at': datetime.now().isoformat(),
                'original_filename': os.path.basename(file_path),
                'file_type': 'document'
            }

            # Добавляем пользовательские метаданные
            if metadata:
                file_metadata.update(metadata)

            # Загружаем файл
            with open(file_path, 'rb') as file:
                self.s3_client.upload_fileobj(
                    file,
                    self.bucket_name,
                    object_key,
                    ExtraArgs={
                        'ContentType': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                        'Metadata': file_metadata
                    }
                )
            print(f"Файл {object_key} загружен")

            return {
                'success': True,
                'object_key': object_key,
                'bucket': self.bucket_name,
                'file_size': os.path.getsize(file_path)
            }

        except Exception as e:
            print(f"Ошибка загрузки файла: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def list_files(self, prefix=''):
        """Просмотр файлов в бакете"""
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )

            if 'Contents' not in response:
                print("Бакет пуст")
                return []

            files = []
            for obj in response['Contents']:
                files.append({
                    'key': obj['Key'],
                    'size': obj['Size'],
                    'last_modified': obj['LastModified']
                })
                print(f"{obj['Key']} ({obj['Size']} байт)")

            return files

        except ClientError as e:
            print(f"Ошибка получения списка файлов: {e}")
            return []

    @staticmethod
    def download_public_file(file_id, save_path="download_route_sheet"):
        try:
            file_url=f"https://storage.yandexcloud.net/trucking-documents/documents/{file_id}_route_sheet.docx"
            response = requests.get(file_url, stream=True)
            response.raise_for_status()

            save_path = f"{save_path}/{file_id}_route_sheet.docx"

            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            print(f"Файл успешно скачан: {save_path}")
            return save_path

        except requests.exceptions.RequestException as e:
            print(f"Ошибка скачивания файла: {e}")
            return None