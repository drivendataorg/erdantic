# Adding New Frameworks

Adding a new data model framework is pretty straightforward. There are three key elements involved, all found in the [`erdantic.base` module](api-reference/base/).

1. [`Field`](../api-reference/base/#erdantic.base.Field): The adapter interface for fields on the data model classes from whatever framework
2. [`Model`](../api-reference/base/#erdantic.base.Model): The adapter interface for those models themselves
3. [`@register_model_adapter`](../api-reference/base/#erdantic.base.register_model_adapter): The decorator you use to register a concrete model adapter so that `erdantic` knows about it

You will be making concrete subclasses of the `Field` and `Model` [abstract base classes](https://docs.python.org/3/library/abc.html) and filling in several abstract methods.

Some tips:

- You can check out the docstrings on the base classes to understand what methods are supposed to do.
- You can also use the source code for the [`erdantic.pydantic`](https://github.com/drivendataorg/erdantic/blob/main/erdantic/pydantic.py) or [`erdantic.dataclasses`](https://github.com/drivendataorg/erdantic/blob/main/erdantic/dataclasses.py) modules as examples.
- The erdantic library is thoroughly type-annotated, so you can use a static typechecker like [mypy](https://mypy.readthedocs.io/en/stable/) to help you ensure correctness.

## Field Subclass

First, make a subclass of `Field`. You can use the template below, which stubs out all of the abstract methods, to get started. You should replace `MyDataField`—both in the class definition and in the `__init__` method definition—with the actual class of field objects in the framework you're adapting. Then fill in the rest of the methods that are being passed.

```python
class MyField(Field[MyDataField]):

    def __init__(self, field: MyDataField):
        if not isinstance(field, MyDataField):
            raise ValueError(f"field must be of type MyDataField. Got: {type(field)}")
        super().__init__(field=field)

    @property
    def name(self) -> str:
        pass

    @property
    def type_obj(self) -> type:
        pass

    def is_many(self) -> bool:
        pass

    def is_nullable(self) -> bool:
        pass
```

## Model Subclass and Decorator

Next, make a subclass of `Model`. It is similarly an abstract base class. Check out the template below with the required methods stubbed. Replace `MyDataClass` in the class declaration and in `__init__` with the actual class of the data class you're adapting.

You'll also need to decorate this class with `@register_model_adapter`. Note that it is actually a decorator factory; calling it with a string input returns the actual decorator. The string input should be a concise unique identifier for your framework, such as the name of its package.

```python
@register_model_adapter("mydataclass")
class MyModel(Model[MyDataClass]):

    def __init__(self, model: Type[MyDataClass]):
        if not self.is_model_type(model):
            raise ValueError(
                "Argument model must be a subclass of MyDataClass. "
                f"Got {repr_type_with_mro(model)}"
            )
        super().__init__(model=model)

    @staticmethod
    def is_model_type(obj: Any) -> bool:
        pass

    @property
    def fields(self) -> List[Field]:
        pass
```
