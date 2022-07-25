#!/usr/bin/env python
import dataclasses

import tormdb


@dataclasses.dataclass
class Person:
    name: str
    age: int


@dataclasses.dataclass
class Family:
    wife: Person
    husband: Person


wife: Person = Person('Catherine', 24)
husband: Person = Person('Chris', 24)

family: Family = Family(
    wife=wife,
    husband=husband)

tormdb.save(family, 'save-example.db')


wife: Person = Person('Amanda', 21)

family2: Family = Family(
    wife=wife,
    husband=wife)

tormdb.save(family2, 'save-example.db')
