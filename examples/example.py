#!/usr/bin/env python
import dataclasses
from typing import List, Optional

import tormdb


@dataclasses.dataclass
class Person:
    name: str
    age: int


@dataclasses.dataclass
class Family:
    husband: Person
    wife: Person
    children: List[Person] = dataclasses.field(default_factory=list)


family: Optional[Family] = tormdb.load([Family, Person])
print(family)

wife: Person = Person('Catherine', 24)
husband: Person = Person('Chris', 24)
daughter: Person
son: Person
daughter = son = Person('Alex', 0)

family = Family(
    husband=husband,
    wife=wife,
    children=[daughter, son])

tormdb.save(family)
print(tormdb.load([Family, Person]))
