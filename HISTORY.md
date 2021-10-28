# erdantic Changelog

## v0.3.0 (2021-10-28)

- Fixed handling of forward references in field type declarations. Evaluated forward references will be properly identified. Unevaluated forward references will throw an `UnevaluatedForwardRefError` with instructions for how to resolve. ([Issue #40](https://github.com/drivendataorg/erdantic/issues/40), [PR #41](https://github.com/drivendataorg/erdantic/issues/41))
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
