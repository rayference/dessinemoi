# Dessine-moi, a simple Python factory

> S'il vous plaît, dessine-moi un mouton.

The narrator of Antoine de Saint-Exupéry's Little Prince probably dreamt of a factory like this one...

*Dessine-moi* is a simple Python factory. We don't have docs **yet** (coming soon!), please read the tests for usage.

Requires Python 3.7+. Tested with Pytest, only dependency is attrs.

## Example

Super lazy usage (you don't even have to create a `Factory` object):

```python
import attr
import dessinemoi

@dessinemoi.register
@attr.s
class Sheep:
    _TYPE_ID = "mouton"
    wool = attr.ib(default="some")

merino = dessinemoi.new("mouton", kwargs={"wool": "lots"})
```

This is however usable only if you are sure that none of your dependencies or no package depending on your code will use *Dessine-moi* as well: there could be name collisions otherwise. In that case, just create a `Factory` instance:

```python
import attr
import dessinemoi

factory = dessinemoi.Factory()

@factory.register
@attr.s
class Sheep:
    _TYPE_ID = "mouton"
    wool = attr.ib(default="some")

merino = factory.new("mouton", kwargs={"wool": "lots"})
```

## License

*Dessine-moi* is distributed under the terms of the
[MIT license](https://choosealicense.com/licenses/mit/).

## About

*Dessine-moi* is written and maintained by [Vincent Leroy](https://github.com/leroyvn).
