from typing import Dict, Type, Optional
import os

from .interface import TemplateData, TemplateDB
from .local_implem import LocalTemplateDB
from .minio_implem import MinioInfos, MinioTemplateDB

engines: Dict[str, Type[TemplateDB]] = {
    's3': MinioTemplateDB,
    'local': LocalTemplateDB,
}

def is_variable_true(variable_name: str) -> Optional[bool]:
    value = os.environ.get(variable_name)
    if value is None:
        return None
    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False
    return None 

if not is_variable_true("DISABLE_GIT"):
    from .git_implem import GITImplem
    engines["git"] = GITImplem

def add_engine(name: str, engine: Type[TemplateDB]) -> None:
    engines[name] = engine
