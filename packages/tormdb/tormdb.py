import inspect
from typing import Any, Union
import uuid

import dataset


def load(db: str):
    pass


def save(db: Union[str, dataset.Database], obj: Any) -> str:
    if not isinstance(db, dataset.Database):
        db_ins: dataset.Database
        with dataset.connect(f'sqlite:///{db}?check_same_thread=False') as db_ins:
            db_ins.executable.execute('PRAGMA journal_mode=WAL')
            return save(db_ins, obj)

    ident: str = str(uuid.uuid4())[:8]
    attr: str
    val: Any
    for attr, val in vars(obj):

        if attr.startswith('_'):
            print(f'{attr=} starts with _')
            continue

        if callable(val) and not inspect.isclass(val):
            print(f'{attr=} is a callable')
            continue

        if not inspect.isclass(val):
            print(f'{attr=} is a {type(val)}')
            db[f'{obj.__name__}#{ident}'].insert(
                dict(name=attr, type=type(val), value=val))

        print(f'{attr=} is {val.__name__}')
        type_name: str = save(db, val)
        db[f'{obj.__name__}#{ident}'].insert(
            dict(name=attr, type=type_name, value=save(db, val)))

    return f'{obj.__name__}#{ident}'
