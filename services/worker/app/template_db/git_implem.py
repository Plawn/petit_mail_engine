import logging
import shutil
from dataclasses import dataclass
from typing import Any, Optional
import uuid

import pygit2

from . import utils
from .interface import TemplateDB


@dataclass
class GitForm:
    url: str
    username: str
    password: str


class GITImplem(TemplateDB):
    def __init__(self, infos: GitForm, logger: Optional[logging.Logger] = None):
        super().__init__(infos, logger)
        self._pulled = False
        self.form = infos
        self.__uuid = uuid.uuid4().hex
        self.folder = self.__uuid

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
        for full_path in utils.iterate_over_folder(self.folder, ['html']):
            try:
                filename = full_path.replace(self.folder + '/', '')
                with open(full_path, 'r') as f:
                    self.logger.info(f'opening {filename}')
                    self.add_template_from_text(
                        filename, f.read(), is_common=utils.is_common_template(filename)
                    )
                    self.logger.info(f'opened {filename}')
            except:
                import traceback
                traceback.print_exc()
                self.logger.error(f'failed {full_path}')
        # remove the folder now that required data is loaded
        shutil.rmtree(self.folder)
