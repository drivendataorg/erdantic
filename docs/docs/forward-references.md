# Handling Forward References

[Forward references](https://www.python.org/dev/peps/pep-0484/#forward-references) are type annotations which use a string literal to declare a name that hasn't been defined yet in the code. The annotation is stored as just the name and the reference to the object is resolved later. Forward references are often useful when a class' type hints need to reference itself, or when you need to avoid a circular import through `if typing.TYPE_CHECKING`.

Dealing with forward reference resolution is somewhat tricky. In the best case, your forward references are already resolved, and erdantic will work without any issue. Otherwise, the following sections will provide some examples of expected errors and what to do.

## Unevaluated Forward References

Forward references must be evaluated along with the right namespace in order to properly resolve them to the correct class. If you are using forward references and they are unresolved, erdantic will error with an `UnevaluatedForwardRefError`. The exception message will provide some information about how to resolve the forward references.

=== "Pydantic"

    ```python
    from typing import List

    import erdantic as erd
    from pydantic import BaseModel


    class Container(BaseModel):
        contains: List["Item"]


    class Item(BaseModel):
        name: str

    # Error because forward reference is unresolved
    diagram = erd.create(Container)
    #> Traceback (most recent call last):
    #>   File "<string>", line 2, in <module>
    #>   File "/Users/jqi/repos/erdantic/erdantic/erd.py", line 192, in create
    #>     search_composition_graph(model=model, seen_models=seen_models, seen_edges=seen_edges)
    #>   File "/Users/jqi/repos/erdantic/erdantic/erd.py", line 241, in search_composition_graph
    #>     raise UnevaluatedForwardRefError(
    #> erdantic.exceptions.UnevaluatedForwardRefError: Unevaluated forward reference 'Item' for field contains on model Container. Call 'update_forward_refs' after model is created to resolve. See: https://pydantic-docs.helpmanual.io/usage/postponed_annotations/

    # Explicitly force evaluation
    Container.update_forward_refs(**locals())

    # Now this works fine
    diagram = erd.create(Container)
    diagram.edges
    #> [ Edge(source=PydanticModel(Container), source_field=<PydanticField: 'contains', List[Item]>, target=PydanticModel(Item))]
    ```

=== "dataclasses"

    ```python
    from dataclasses import dataclass
    from typing import get_type_hints, List

    import erdantic as erd


    @dataclass
    class Container:
        contains: List["Item"]


    @dataclass
    class Item:
        name: str


    # Error because forward reference is unresolved
    diagram = erd.create(Container)
    #> Traceback (most recent call last):
    #>   File "/Users/jqi/miniconda3/envs/erdantic39/lib/python3.9/site-packages/reprexlite/code.py", line 71, in evaluate
    #>     exec(str(self).strip(), scope, scope)
    #>   File "<string>", line 2, in <module>
    #>   File "/Users/jqi/repos/erdantic/erdantic/erd.py", line 192, in create
    #>     search_composition_graph(model=model, seen_models=seen_models, seen_edges=seen_edges)
    #>   File "/Users/jqi/repos/erdantic/erdantic/erd.py", line 241, in search_composition_graph
    #>     raise UnevaluatedForwardRefError(
    #> erdantic.exceptions.UnevaluatedForwardRefError: Unevaluated forward reference 'Item' for field contains on model Container. Call 'typing.get_type_hints' on your dataclass after creating it to resolve.

    # Explicitly force evaluation
    _ = get_type_hints(Container, localns=locals())

    # Now this works fine
    diagram = erd.create(Container)
    diagram.edges
    #> [ Edge(source=DataClassModel(Container), source_field=<DataClassField: 'contains', List[Item]>, target=DataClassModel(Item))]
    ```


## Untransformed String Forward References

Under the hood, forward references usually—but not always—get converted from a string to a `typing.ForwardRef` (or in Python <3.7.4, `typing._ForwardRef`) instances. These objects track metadata about the type annotation, including what they get evaluated to.

Unfortunately, sometimes the annotations remain as unconverted strings, and erdantic is unable to handle those cases. In such cases, erdantic will error with a `StringForwardRefError`. To work around that, you can explicitly declare those annotations with `typing.ForwardRef` (or `typing._ForwardRef` for Python <3.7.4).

=== "Pydantic"

    Pydantic does this automatically and doesn't need any further intervention.

    ```python
    import erdantic as erd
    from pydantic import BaseModel


    class SingleContainer(BaseModel):
        contains: "Item"


    class Item(BaseModel):
        name: str

    # Works without any issues
    SingleContainer.update_forward_refs(**locals())
    diagram = erd.create(SingleContainer)
    diagram.edges
    #> [ Edge(source=PydanticModel(SingleContainer), source_field=<PydanticField: 'contains', Item>, target=PydanticModel(Item))]
    ```

=== "dataclasses"

    dataclasses sometimes do not convert from strings and require explicit use of `typing.ForwardRef`.

    ```python
    from dataclasses import dataclass
    from typing import get_type_hints, ForwardRef

    import erdantic as erd


    @dataclass
    class SingleContainer:
        contains: "Item"


    @dataclass
    class Item:
        name: str


    # Errors because string annotation is unconverted
    _ = get_type_hints(SingleContainer, localns=locals())
    diagram = erd.create(SingleContainer)
    #> Traceback (most recent call last):
    #>   File "<string>", line 1, in <module>
    #>   File "/Users/jqi/repos/erdantic/erdantic/erd.py", line 192, in create
    #>     search_composition_graph(model=model, seen_models=seen_models, seen_edges=seen_edges)
    #>   File "/Users/jqi/repos/erdantic/erdantic/erd.py", line 245, in search_composition_graph
    #>     raise StringForwardRefError(
    #> erdantic.exceptions.StringForwardRefError: Forward reference 'Item' for field 'contains' on model 'SingleContainer' is a string literal and not a typing.ForwardRef object. erdantic is unable to handle forward references that aren't transformed into typing.ForwardRef. Declare explicitly with 'typing.ForwardRef("Item", is_argument=False)'.


    @dataclass
    class FixedSingleContainer:
        contains: ForwardRef("Item", is_argument=False)


    # Now this works fine
    _ = get_type_hints(FixedSingleContainer, localns=locals())
    diagram = erd.create(FixedSingleContainer)
    diagram.edges
    #> [ Edge(source=DataClassModel(FixedSingleContainer), source_field=<DataClassField: 'contains', Item>, target=DataClassModel(Item))]
    ```

<sup>Examples created with [reprexlite](https://github.com/jayqi/reprexlite).</sup>
