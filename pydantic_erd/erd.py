from typing import List, Set, Type

from pydantic import BaseModel
from pydantic.fields import ModelField


row_template = """\
    <tr><td>{name}</td><td port="{name}">{type_name}</td></tr>\
"""


class Field(BaseModel):
    pydantic_field: ModelField

    class Config:
        arbitrary_types_allowed = True

    @property
    def name(self):
        return self.pydantic_field.name

    @property
    def type_name(self):
        return self.pydantic_field._type_display()

    @property
    def type_obj(self):
        return self.pydantic_field.type_

    def dot(self):
        return row_template.format(name=self.name, type_name=self.type_name)

    def __hash__(self):
        return id(self.pydantic_field)

    def __eq__(self, other):
        return isinstance(other, type(self)) and self.__hash__ == other.__hash__


table_template = """\
{name} [label=<
  <table border="0" cellborder="1" cellspacing="0">
    <tr><td port="_root" colspan="2"><b>{name}</b></td></tr>
{rows}
  </table>
>];
"""


class Model(BaseModel):
    pydantic_model: Type[BaseModel]

    class Config:
        arbitrary_types_allowed = True

    @property
    def name(self):
        return self.pydantic_model.__name__

    @property
    def fields(self) -> List[Field]:
        return [Field(pydantic_field=f) for f in self.pydantic_model.__fields__.values()]

    def dot(self):
        rows = "\n".join(field.dot() for field in self.fields)
        return table_template.format(name=self.name, rows=rows)

    def __hash__(self):
        return id(self.pydantic_model)

    def __eq__(self, other):
        return isinstance(other, type(self)) and self.__hash__ == other.__hash__


edge_template = "{source}:{source_field}:e -> {target}:_root:w;"


class Edge(BaseModel):
    source: Model
    source_field: Field
    target: Model

    def dot(self):
        return edge_template.format(
            source=self.source.name, source_field=self.source_field.name, target=self.target.name
        )

    def __hash__(self):
        return hash((self.source, self.source_field, self.target))

    def __eq__(self, other):
        return isinstance(other, type(self)) and hash(self) == hash(other)


diagram_template = """\
digraph {{
  graph [nodesep="0.5", ranksep="1.5"];
  node [shape=plain]
  rankdir=LR;

{tables}
{edges}
}}
"""


class EntityRelationshipDiagram(BaseModel):
    models: Set[Model]
    edges: Set[Edge]

    @classmethod
    def from_pydantic_models(cls, *models):
        seen_models = set()
        seen_edges = set()
        for model in models:
            cls.search(model, seen_models, seen_edges)
        return cls(models=seen_models, edges=seen_edges)

    @classmethod
    def search(cls, pydantic_model: BaseModel, seen_models: Set[Model], seen_edges: Set[Edge]):
        model = Model(pydantic_model=pydantic_model)
        if model not in seen_models:
            seen_models.add(model)
            for field in model.fields:
                if issubclass(field.type_obj, BaseModel):
                    field_model = cls.search(field.type_obj, seen_models, seen_edges)
                    seen_edges.add(Edge(source=model, source_field=field, target=field_model))
        return model

    def dot(self):
        tables = "\n".join(table.dot() for table in self.models)
        edges = "\n".join(edge.dot() for edge in self.edges)
        return diagram_template.format(tables=tables, edges=edges)
