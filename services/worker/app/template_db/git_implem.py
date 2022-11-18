import logging
import shutil
import uuid
from dataclasses import dataclass
from typing import Optional

import pygit2

from .local_implem import LocalInfos, LocalTemplateDB


@dataclass
class GitForm:
    url: str
    username: str
    password: str


class GITImplem(LocalTemplateDB):
    def __init__(self, infos: GitForm, logger: Optional[logging.Logger] = None):
        self.__uuid = uuid.uuid4().hex
        self.temp_folder = self.__uuid
        local_infos = LocalInfos(self.__uuid)
        super().__init__(local_infos, logger)
        self._pulled = False
        self.form = infos

    @staticmethod
    def get_creds_form() -> GitForm:
        return GitForm

    def __pull(self):
        # https://www.pygit2.org/remotes.html?highlight=fetch#pygit2.Remote.fetch
        pygit2.clone_repository(
            self.form.url,
            self.__uuid,
            callbacks=pygit2.RemoteCallbacks(pygit2.UserPass(
                self.form.username, self.form.password))
        )
        self._pulled = True

    def init(self):
        self.__pull()
        super().init()
        shutil.rmtree(self.temp_folder)
