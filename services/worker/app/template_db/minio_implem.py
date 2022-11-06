import io
import logging
from dataclasses import dataclass
from typing import Optional

import minio

from .interface import TemplateDB


@dataclass
class MinioInfos:
    host: str
    passkey: str
    accesskey: str
    bucket_name: str


class MinioTemplateDB(TemplateDB):
    def __init__(self, minio_creds: MinioInfos, logger: Optional[logging.Logger] = None):
        super().__init__(minio_creds, logger=logger)
        self.bucket_name = minio_creds.bucket_name
        self.minio_instance = minio.Minio(
            minio_creds.host, minio_creds.accesskey, minio_creds.passkey
        )

    @staticmethod
    def get_creds_form() -> MinioInfos:
        return MinioInfos

    def init(self):
        buckets = self.minio_instance.list_buckets()
        self.logger.info(f"buckets: {buckets}")
        filenames = (
            obj.object_name for obj in self.minio_instance.list_objects(self.bucket_name, recursive=True)
        )
        for filename in filenames:
            self.logger.info(f'pulling {filename}')
            handle = self.minio_instance.get_object(
                self.bucket_name, filename)
            buf = io.BytesIO()
            for d in handle.stream(32 * 1024):
                buf.write(d)
            buf.seek(0)
            is_common = filename.startswith('common')
            self.add_template_from_text(
                filename, buf.read(), is_common
            )
            self.logger.info(f'Pulled {filename}')
