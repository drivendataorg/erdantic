# Handling forward references

[Forward references](https://www.python.org/dev/peps/pep-0484/#forward-references) are type annotations which use a string literal to declare a name that hasn't been defined yet in the code. The annotation is stored as just the name and the reference to the object is resolved later. Forward references are often useful when a class' type hints need to reference itself, or when you need to avoid a circular import through `if typing.TYPE_CHECKING`.

In general, data modeling frameworks like Pydantic and attrs have functionality to resolve forward references automatically. For erdantic's built-in plugins, the automatic resolution should handle things in most cases without any special input from you. 

## UnresolvableForwardRefError

If you get a [`UnresolvableForwardRefError`][erdantic.exceptions.UnresolvableForwardRefError], that means the automatic resolution failed. Forward references must be evaluated against the right namespace, and in some cases, Python has not kept track of that namespace. The most common way for this to happen is if your model class is defined inside the local scope of a function. The way to resolve it will depend on the particular modeling framework/plugin that you're using. The exception message will tell you what to do. 

## UnevaluatedForwardRefError

If you get a [`UnevaluatedForwardRefError`][erdantic.exceptions.UnevaluatedForwardRefError], that means that fields were extracted from your model without evaluating forward references. 

If your model is using one of erdantic's built-in plugins, then this is unexpected behavior. The built-in plugins should attempt to automatically resolve forward references and should throw an `UnresolvableForwardRefError` as described in the previous section if unable to. Please [open an issue](https://github.com/drivendataorg/erdantic/issues) on our GitHub repository to report this bug. 

If you are using a custom plugin, then your plugin may not be properly resolving forward references. See the ["Field extractor function"](./extending.md#field-extractor-function) section in the documentation about plugins for addressing this.
