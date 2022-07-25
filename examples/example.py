#!/usr/bin/env python
import dataclasses
from typing import Optional

import tormdb


@dataclasses.dataclass
class Person:
    name: str
    age: int


@dataclasses.dataclass
class Family:
    daughter: Person
    husband: Person
    son: Person
    wife: Person


family: Optional[Family] = tormdb.load([Family, Person])
print(family)

wife: Person = Person('Catherine', 24)
husband: Person = Person('Chris', 24)
daughter: Person
son: Person
daughter = son = Person('Alex', 0)

family = Family(
    daughter=daughter,
    husband=husband,
    son=son,
    wife=wife)

tormdb.save(family)
print(tormdb.load([Family, Person]))
