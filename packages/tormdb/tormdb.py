import ctypes
from typing import Any, Dict, List, Set, Type, Union

import dataset

object_id_to_table_name_map: Dict[int, str] = dict()


def get_object_if_exists(table_name: str) -> Any:
    obj_id: int
    name: str
    for obj_id, name in object_id_to_table_name_map.items():
        if name == table_name:
            return ctypes.cast(obj_id, ctypes.py_object).value


def get_table_name(obj: Any, is_root: bool = False) -> str:
    if id(obj) not in object_id_to_table_name_map:
        object_id_to_table_name_map[id(obj)] = type(obj).__name__ if is_root else f'{type(obj).__name__}#{id(obj)}'
    return object_id_to_table_name_map[id(obj)]


def clear_dangling(obj: Any, db: Union[str, dataset.Database] = 'config.db'):
    if not isinstance(db, dataset.Database):
        db_ins: dataset.Database
        with dataset.connect(f'sqlite:///{db}?check_same_thread=False') as db_ins:
            db_ins.executable.execute('PRAGMA journal_mode=WAL')
            return clear_dangling(obj, db_ins)

    associated_table_names: Set[str] = {type(obj).__name__}
    pending_scan_table_names: List[str] = [type(obj).__name__]

    while pending_scan_table_names:
        for row in db[pending_scan_table_names[0]].all():
            if row['type'] == 'Table':
                if row['value'] not in associated_table_names:
                    associated_table_names.add(row['value'])
                    pending_scan_table_names.append(row['value'])
        pending_scan_table_names.pop(0)

    table_name: str
    for table_name in db.tables:
        if table_name not in associated_table_names:
            db[table_name].drop()


def load(classes: List[Type], db: Union[str, dataset.Database] = 'config.db') -> Any:
    if not isinstance(db, dataset.Database):
        db_ins: dataset.Database
        with dataset.connect(f'sqlite:///{db}?check_same_thread=False') as db_ins:
            db_ins.executable.execute('PRAGMA journal_mode=WAL')
            return load(classes, db_ins)
    return load_table(classes[0].__name__, classes, db)


def load_table(table_name: str, classes: List[Type], db: Union[str, dataset.Database] = 'config.db') -> Any:
    if not isinstance(db, dataset.Database):
        db_ins: dataset.Database
        with dataset.connect(f'sqlite:///{db}?check_same_thread=False') as db_ins:
            db_ins.executable.execute('PRAGMA journal_mode=WAL')
            return load_table(table_name, classes, db_ins)

    if table_name not in db:
        return

    obj: Any = get_object_if_exists(table_name)

    if type(obj) == list or table_name.split('#')[0] == 'list':
        l: List[Any] = list()

        row: Dict[str, Any]
        for row in db[table_name].all():
            l.append(load_table(row['value'], classes, db) if row['type'] == 'Table' else row['value'])

        obj = l[:]
        object_id_to_table_name_map[id(l)] = table_name
    else:
        d: Dict[str, Any] = dict()

        row: Dict[str, Any]
        for row in db[table_name].all():
            d[row['name']] = load_table(row['value'], classes, db) if row['type'] == 'Table' else row['value']

        if obj:
            obj.__dict__.update(d)
        else:
            klass: Type
            class_dict: Dict[str, Type] = {klass.__name__: klass for klass in classes}
            obj = class_dict[table_name.split('#')[0]](**d)
            object_id_to_table_name_map[id(obj)] = table_name

    return obj


def save(obj: Any, db: Union[str, dataset.Database] = 'config.db', is_root: bool = True) -> str:
    if not isinstance(db, dataset.Database):
        db_ins: dataset.Database
        with dataset.connect(f'sqlite:///{db}?check_same_thread=False') as db_ins:
            db_ins.executable.execute('PRAGMA journal_mode=WAL')
            return save(obj, db_ins, is_root)

    if is_root:
        object_id_to_table_name_map.clear()

    table_name: str = get_table_name(obj, is_root)

    if type(obj) == list:
        i: int
        val: Any
        for i, val in enumerate(obj):
            if val.__class__.__module__ == 'builtins' and type(val) != list:
                db[table_name].upsert(dict(name=str(i), type=type(val).__name__, value=val), ['name'])
                continue

            db[table_name].upsert(dict(name=str(i), type='Table', value=save(val, db, False)), ['name'])
    else:
        attr: str
        val: Any
        for attr, val in vars(obj).items():
            if attr.startswith('_'):
                continue

            if callable(val):
                continue

            if val.__class__.__module__ == 'builtins' and type(val) != list:
                db[table_name].upsert(dict(name=attr, type=type(val).__name__, value=val), ['name'])
                continue

            db[table_name].upsert(dict(name=attr, type='Table', value=save(val, db, False)), ['name'])

    if is_root:
        clear_dangling(obj, db)

    return table_name
