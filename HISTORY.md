# erdantic Changelog

## v0.2.1 (2021-02-16)

- Fixed runtime error when rendering a data model that had a field containing `typing.Any`. ([#25](https://github.com/drivendataorg/erdantic/issues/25), [#26](https://github.com/drivendataorg/erdantic/issues/26))

## v0.2.0 (2021-02-14)

- Added option to specify models as terminal nodes. This allows you to truncate large diagrams and split them up into smaller ones. ([#24](https://github.com/drivendataorg/erdantic/pull/24))

## v0.1.2 (2021-02-10)

- Fixed bug where Pydantic fields were missing generics in their type annotations. ([#19](https://github.com/drivendataorg/erdantic/pull/19))
- Added tests against static rendered DOT output. Change adapter tests to use parameterized fixtures. ([#21](https://github.com/drivendataorg/erdantic/pull/21))

## v0.1.1 (2021-02-10)

- Fixed rendered example image in the package description on PyPI. ([#18](https://github.com/drivendataorg/erdantic/pull/18))

## v0.1.0 (2021-02-10)

Initial release! 🎉
