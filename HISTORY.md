# erdantic Changelog

## v1.0.5 (2024-09-19)

- Fixed runtime `AttributeError` that occurred when creating a diagram that includes a model with a field that uses a type annotation with the ellipsis literal (e.g., `tuple[int, ...]`). ([Issue #124](https://github.com/drivendataorg/erdantic/issues/124), [PR #127](https://github.com/drivendataorg/erdantic/pull/127))

## v1.0.4 (2024-07-16)

- Fixed handling of `typing.Annotated` in cases where it's not the outermost generic type. ([Issue #122](https://github.com/drivendataorg/erdantic/issues/122), [PR #123](https://github.com/drivendataorg/erdantic/pull/123))

## v1.0.3 (2024-05-10)

- Fixed `StopIteration` error when rendering a model that has no fields. ([Issue #120](https://github.com/drivendataorg/erdantic/issues/120), [PR #121](https://github.com/drivendataorg/erdantic/pull/121))

## v1.0.2 (2024-04-11)

- Fixed `AttributeError` when adding a model that has a field annotated with certain typing special forms like `Any`, `Literal`, or `TypeVar` instances. ([Issue #114](https://github.com/drivendataorg/erdantic/issues/114), [PR #115](https://github.com/drivendataorg/erdantic/pull/115))

## v1.0.1 (2024-04-10)

- Fixed `ModuleNotFoundError` when importing from `erdantic.examples` without attrs installed.

## v1.0.0.post2 (2024-04-10)

- Fixed missing LICENSE file in sdist.

## v1.0.0.post1 (2024-04-09)

- Fixed outdated note in README.

## v1.0.0 (2024-04-09)

> [!IMPORTANT]
> This release features significant changes to erdantic, primarily to the backend process of analyzing models and representing data. If you have been primarily using the CLI or the convenience functions `create`, `draw`, and `to_dot`, then your code may continue to work without any changes. If you are doing something more advanced, you may need to update your code.

### CLI changes

- Deprecated `--termini` option. Use the new `--terminal-model` option instead. The shorthand option `-t` remains the same. The `--termini` option still works but will emit a deprecation warning.

### Convenience function changes

- Deprecated `termini` argument for `create`, `draw`, and `to_dot` functions. Use the new `terminal_models` argument instead. The `termini` argument still works but will emit a deprecation warning.
- Added `graph_attr`, `node_attr`, and `edge_attr` arguments to the `draw` and `to_dot` functions that allow you to override attributes on the generated pygraphviz object for the diagram.

### Visual changes

A few changes have been made to the visual content of rendered diagrams.

- Changed the extraction of type names to use the [typenames](https://github.com/jayqi/typenames) library. This should generally produce identical rendered outputs as before, with the following exception:
    - Removed the special case behavior for rendering enum classes. Enums now just show the class name without inheritance information.
- Changed collection fields (e.g., `List[TargetModel]`) to display as a "many" relationship (crow) instead of a "zero-or-many" relationship (odot + crow), treating the modality of the field as unspecified. A field will only be displayed as "zero-or-many" (odot + crow) if it is explicitly optional, like `Optional[List[TargetModel]]`.
- Fixed incorrect representation of manyness for type annotations where the outermost annotation wasn't a collection type. ([Issue #105](https://github.com/drivendataorg/erdantic/issues/105))

### Support for attrs

- Added support for [attrs](https://www.attrs.org/en/stable/index.html) classes, i.e., classes decorated by `attrs.define`. The source code for attrs support can be found in the new module `erdantic.plugins.attrs`.
- Added new example module `erdantic.examples.attrs`.

### Backend changes

Significant changes have been made to the library backend to more strongly separate the model analysis process, the extracted data, and the diagram rendering process. We believe this more structured design facilitates customizing diagrams and simplifies the implementation for each data modeling framework. Please see the new documentation pages ["Customizing diagrams"](http://erdantic.drivendata.org/v1.0/customizing/) and ["Extending or modifying erdantic"](http://erdantic.drivendata.org/v1.0/extending/) for details on the new design.

A summary of some key changes is below:

- Removed the adapter base classes `Model` and `Field` and the conrete adapters `DataClassModel`, `DataClassField`, `PydanticModel`, and `PydanticField`.
  - Added new Pydantic models `ModelInfo` and `FieldInfo` to replace the adapter system. These new models hold static data that have been extracted from models that erdantic analyzed.
- Removed the adapter system and associated objects such as `model_adapter_registry` and `register_model_adapter`.
  - Added new plugin system to replace the adapter system as the way that modeling frameworks are supported. Plugins must implement two functions—a predicate function and a field extractor function—and be registered using `register_plugin`. All objects related to plugins can be found in the new `erdantic.plugins` module and its submodules.
- Renamed `erdantic.typing` module to `erdantic.typing_utils`.

### Other

- Added [PEP 561 `py.typed` marker file](https://peps.python.org/pep-0561/#packaging-type-information) to indicate that the package supports type checking.
- Added IPython special method for pretty-print string representations of `EntityRelationshipDiagram` instances.
- Removed support for Python 3.7. ([PR #102](https://github.com/drivendataorg/erdantic/pull/102))

## v0.7.1 (2024-04-09)

This will be the last version that supports Python 3.7.

- Added version typer version ceiling of `< 0.10.0` due to incompatibility with a fix introduced in that version.


## v0.7.0 (2024-02-11)

- Added support for Pydantic V1 legacy models. These are models created from the `pydantic.v1` namespace when Pydantic V2 is installed. ([PR #94](https://github.com/drivendataorg/erdantic/pull/94) from [@ursereg](https://github.com/ursereg))

## v0.6.0 (2023-07-09)

- Added support for Pydantic V2.
- Removed support for Pydantic V1.
- Changed the init signature for `PydanticField` to work with Pydantic V2's API.
- Added `is_many` and `is_nullable` functions to `erdantic.typing`.

## v0.5.1 (2023-07-04)

- Changed Pydantic dependency to be `< 2`. This will be the final version of erdantic that supports Pydantic V1.
- Changed to pyproject.toml-based build.

## v0.5.0 (2022-07-29)

- Removed support for Python 3.6. ([Issue #51](https://github.com/drivendataorg/erdantic/issues/51), [PR #56](https://github.com/drivendataorg/erdantic/pull/56))
- Added support for modules as inputs to all entrypoints to diagram creation (`create`, `draw`, `to_dot`, CLI). For all modules passed, erdantic will find all supported data model classes in each module. ([Issue #23](https://github.com/drivendataorg/erdantic/issues/23), [PR #58](https://github.com/drivendataorg/erdantic/pull/58))
    - Added new parameter `limit_search_models_to` to all entrypoints to allow for limiting which data model classes will be yielded from searching a module.


## v0.4.1 (2022-04-08)

- Fixed error when rendering a data model that has field using `typing.Literal`. ([PR #49](https://github.com/drivendataorg/erdantic/pull/49))

## v0.4.0 (2021-11-06)

- Added support for showing field documentation from Pydantic models with descriptions set with `Field(description=...)` in SVG tooltips. This will add an "Attributes" section to the tooltip using Google-style docstring format and lists fields where the `description` keyword argument is used. ([Issue #8](https://github.com/drivendataorg/erdantic/issues/8#issuecomment-958905131), [PR #42](https://github.com/drivendataorg/erdantic/pull/42))

## v0.3.0 (2021-10-28)

- Fixed handling of forward references in field type declarations. Evaluated forward references will be properly identified. Forward references not converted to `typing.ForwardRef` will throw a `StringForwardRefError` with instructions for how to resolve. Unevaluated forward references will throw an `UnevaluatedForwardRefError` with instructions for how to resolve. See [new documentation](https://erdantic.drivendata.org/stable/forward-references/) for more details. ([Issue #40](https://github.com/drivendataorg/erdantic/issues/40), [PR #41](https://github.com/drivendataorg/erdantic/pull/41))
- Changed name of `erdantic.errors` module to `erdantic.exceptions`. ([PR #41](https://github.com/drivendataorg/erdantic/issues/41))
- Added new `ErdanticException` base class from which other exceptions raised within the erdantic library are subclassed from. Changed several existing `ValueError` exceptions to new exception classes that subclass both `ErdanticException` and `ValueError`. ([PR #41](https://github.com/drivendataorg/erdantic/issues/41))
- Changed `__lt__` method on `Model` and `Edge` to return `NotImplemented` instead of raising an exception to follow typical convention for unsupported input types. ([PR #41](https://github.com/drivendataorg/erdantic/issues/41))

## v0.2.1 (2021-02-16)

- Fixed runtime error when rendering a data model that had a field containing `typing.Any`. ([Issue #25](https://github.com/drivendataorg/erdantic/issues/25), [PR #26](https://github.com/drivendataorg/erdantic/issues/26))

## v0.2.0 (2021-02-14)

- Added option to specify models as terminal nodes. This allows you to truncate large diagrams and split them up into smaller ones. ([PR #24](https://github.com/drivendataorg/erdantic/pull/24))

## v0.1.2 (2021-02-10)

- Fixed bug where Pydantic fields were missing generics in their type annotations. ([PR #19](https://github.com/drivendataorg/erdantic/pull/19))
- Added tests against static rendered DOT output. Change adapter tests to use parameterized fixtures. ([PR #21](https://github.com/drivendataorg/erdantic/pull/21))

## v0.1.1 (2021-02-10)

- Fixed rendered example image in the package description on PyPI. ([PR #18](https://github.com/drivendataorg/erdantic/pull/18))

## v0.1.0 (2021-02-10)

Initial release! 🎉
