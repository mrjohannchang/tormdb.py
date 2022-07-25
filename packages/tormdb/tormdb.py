from typing import Any, Dict, Union

import dataset


obj_to_stored_map: Dict[int, str] = dict()
stored_to_obj_map: Dict[str, int] = dict()


def get_ident(obj: Union[Any]) -> str:
    if id(obj) not in obj_to_stored_map:
        obj_to_stored_map[id(obj)] = str(id(obj))
        stored_to_obj_map[str(id(obj))] = id(obj)
    return obj_to_stored_map[id(obj)]


def load(db: str):
    pass


def load_ident(obj: str):
    pass


def save(obj: Any, db: Union[str, dataset.Database]) -> str:
    print(f'{db=}, {obj=}')

    if not isinstance(db, dataset.Database):
        db_ins: dataset.Database
        with dataset.connect(f'sqlite:///{db}?check_same_thread=False') as db_ins:
            db_ins.executable.execute('PRAGMA journal_mode=WAL')
            return save(obj, db_ins)

    attr: str
    val: Any
    for attr, val in vars(obj).items():
        if attr.startswith('_'):
            print(f'{attr} starts with _')
            continue

        if callable(val):
            print(f'{attr} is a callable')
            continue

        if val.__class__.__module__ == 'builtins':
            print(f'{attr} is an instance of the built-in class {type(val).__name__}')
            db[f'{type(obj).__name__}#{get_ident(obj)}'].upsert(
                dict(name=attr, type=type(val).__name__, value=val), ['name', 'value'])
            continue

        print(f'{attr} is an instance of {type(val).__name__}')
        db[f'{type(obj).__name__}#{get_ident(obj)}'].upsert(
            dict(name=attr, type=type(val).__name__, value=save(val, db)), ['name', 'value'])

    return f'{type(obj).__name__}#{get_ident(obj)}'
