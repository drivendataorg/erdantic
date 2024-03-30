import erdantic as erd
import erdantic.examples.attrs as attr_examples
import erdantic.examples.dataclasses as dataclass_examples
import erdantic.examples.pydantic as pydantic_examples
import erdantic.examples.pydantic_v1 as pydantic_v1_examples

erd.create(attr_examples.Party)
erd.create(attr_examples)

erd.create(dataclass_examples.Party)
erd.create(dataclass_examples)

erd.create(pydantic_examples.Party)
erd.create(pydantic_examples)

erd.create(pydantic_v1_examples.Party)
erd.create(pydantic_v1_examples)
