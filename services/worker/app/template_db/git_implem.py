import logging
from dataclasses import dataclass
from typing import Any, Optional
from uuid import uuid4
import pygit2

from . import utils
from .interface import TemplateDB


class LoginCallback(pygit2.RemoteCallbacks):
    def __init__(self, credentials=None, certificate=None):
        super().__init__(credentials, certificate)

    def transfer_progress(self, stats: pygit2.remote.TransferProgress):
        print(f'{stats.indexed_objects}/{stats.total_objects}')


@dataclass
class GitForm:
    url: str
    username: str
    password: str


class GITImplem(TemplateDB):
    def __init__(self, infos: GitForm, logger: Optional[logging.Logger] = None):
        super().__init__(infos, logger)
        self.form = infos
        self.__uuid = uuid4()
        self.folder = self.__uuid

    @staticmethod
    def get_creds_form() -> GitForm:
        return GitForm

    def __pull(self):
        # https://www.pygit2.org/remotes.html?highlight=fetch#pygit2.Remote.fetch
        pygit2.clone_repository(
            self.form.url,
            self.__uuid,
            callbacks=LoginCallback(pygit2.UserPass(self.form.username, self.form.password))
        )
        # copy in memory
        # delete
        # after init
        self._pulled = True

    def init(self):
        self.__pull()
        for full_path in utils.iterate_over_folder(self.folder):
            try:
                filename = full_path.replace(self.folder + '/', '')
                with open(full_path, 'r') as f:
                    self.logger.info(f'opening {filename}')
                    self.add_template_from_text(
                        filename, f.read(), filename.startswith('common')
                    )
                    self.logger.info(f'opened {filename}')
            except:
                import traceback
                traceback.print_exc()
                self.logger.error(f'failed {full_path}')
        # TODO: remove full folder


# class MinioTemplateDB(TemplateDB):
#     def __init__(self, minio_creds: MinioInfos, logger: Optional[logging.Logger] = None):
#         super().__init__(minio_creds, logger=logger)
#         self.bucket_name = minio_creds.bucket_name
#         self.minio_instance = minio.Minio(
#             minio_creds.host, minio_creds.accesskey, minio_creds.passkey
#         )

#     @staticmethod
#     def get_creds_form() -> MinioInfos:
#         return MinioInfos
