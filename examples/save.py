#!/usr/bin/env python
import dataclasses

import tormdb


@dataclasses.dataclass
class Person:
    name: str
    age: int


p: Person = Person('Catherine', 24)

tormdb.save(p)
