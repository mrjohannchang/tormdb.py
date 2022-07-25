# tormdb

`tormdb` stands for Transposed Object Relational Mapping Database.

## Usage

### Save

```
import dataclasses
from typing import List

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
```

### Load

```
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
```
