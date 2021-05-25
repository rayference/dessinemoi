# Dessine-moi, a simple Python factory

> S'il vous plaît, dessine-moi un mouton.

The narrator of the Little Prince probably dreamt of a factory like this one...

*Dessine-moi* is a simple Python factory. We don't have docs **yet** (coming soon!), please read the tests for usage.

Requires Python 3.7+. Tested with Pytest, only dependency is attrs.

## Example

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

## License

This library is MIT-licensed.

## About

*Dessine-moi* is written and maintained by Vincent Leroy.
