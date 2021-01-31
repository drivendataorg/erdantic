import os
from typing import List, Set, Type, Union

import pygraphviz as pgv

from pydantic import BaseModel
from pydantic.fields import ModelField


row_template = """<tr><td>{name}</td><td port="{name}">{type_name}</td></tr>"""


class Field(BaseModel):
    pydantic_field: ModelField

    class Config:
        arbitrary_types_allowed = True

    @property
    def name(self) -> str:
        return self.pydantic_field.name

    @property
    def type_name(self) -> str:
        return self.pydantic_field._type_display()

    @property
    def type_obj(self) -> type:
        return self.pydantic_field.type_

    def dot_row(self) -> str:
        return row_template.format(name=self.name, type_name=self.type_name)

    def __hash__(self):
        return id(self.pydantic_field)

    def __eq__(self, other):
        return isinstance(other, type(self)) and self.__hash__ == other.__hash__


table_template = """
<<table border="0" cellborder="1" cellspacing="0">
<tr><td port="_root" colspan="2"><b>{name}</b></td></tr>
{rows}
</table>>
"""


class Model(BaseModel):
    pydantic_model: Type[BaseModel]

    @property
    def name(self) -> str:
        return self.pydantic_model.__name__

    @property
    def fields(self) -> List[Field]:
        return [Field(pydantic_field=f) for f in self.pydantic_model.__fields__.values()]

    def dot_label(self) -> str:
        rows = "\n".join(field.dot_row() for field in self.fields)
        return table_template.format(name=self.name, rows=rows).replace("\n", "")

    def __hash__(self):
        return id(self.pydantic_model)

    def __eq__(self, other):
        return isinstance(other, type(self)) and hash(self) == hash(other)


class Edge(BaseModel):
    source: Model
    source_field: Field
    target: Model

    def dot_arrowhead(self) -> str:
        is_many = self.source_field.pydantic_field.shape > 1
        is_nullable = self.source_field.pydantic_field.allow_none
        cardinality = "crow" if is_many else "nonetee"
        modality = "odot" if is_nullable or is_many else "tee"
        return cardinality + modality

    def __hash__(self):
        return hash((self.source, self.source_field, self.target))

    def __eq__(self, other):
        return isinstance(other, type(self)) and hash(self) == hash(other)


class EntityRelationshipDiagram(BaseModel):
    models: Set[Model]
    edges: Set[Edge]

    @classmethod
    def from_pydantic_models(cls, *models: Type[BaseModel]):
        seen_models = set()
        seen_edges = set()
        for model in models:
            cls.search(model, seen_models, seen_edges)
        return cls(models=seen_models, edges=seen_edges)

    @classmethod
    def search(
        cls, pydantic_model: BaseModel, seen_models: Set[Model], seen_edges: Set[Edge]
    ) -> Model:
        model = Model(pydantic_model=pydantic_model)
        if model not in seen_models:
            seen_models.add(model)
            for field in model.fields:
                if issubclass(field.type_obj, BaseModel):
                    field_model = cls.search(field.type_obj, seen_models, seen_edges)
                    seen_edges.add(Edge(source=model, source_field=field, target=field_model))
        return model

    def draw(self, path: Union[str, os.PathLike], **kwargs):
        return self.graph().draw(path, prog="dot", **kwargs)

    def graph(self) -> pgv.AGraph:
        g = pgv.AGraph(directed=True, nodesep=0.5, ranksep=1.5, rankdir="LR")
        g.node_attr["shape"] = "plain"
        for model in self.models:
            g.add_node(model.name, label=model.dot_label())
        for edge in self.edges:
            g.add_edge(
                edge.source.name,
                edge.target.name,
                tailport=f"{edge.source_field.name}:e",
                headport="_root:w",
                arrowhead=edge.dot_arrowhead(),
            )
        return g

    def to_dot(self) -> str:
        return self.graph().string()

    def _repr_svg_(self):
        graph = self.graph()
        return graph.draw(prog="dot", format="svg").decode(graph.encoding)


def draw(*models: Type[BaseModel], path: Union[str, os.PathLike], **kwargs):
    diagram = EntityRelationshipDiagram.from_pydantic_models(*models)
    diagram.draw(path=path, **kwargs)


def to_dot(*models: Type[BaseModel]):
    diagram = EntityRelationshipDiagram.from_pydantic_models(*models)
    return diagram.to_dot()
