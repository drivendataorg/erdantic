# erdantic Changelog

## v0.7.0 (2024-02-11)

This will be the last version that supports Python 3.7.

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
