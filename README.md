# mobi-plugin

Popcorn/mbipy interface on Napari for synchrotron experiments

----------------------------------

This [napari] plugin was generated with [copier] using the [napari-plugin-template].

<!--
Don't miss the full getting started guide to set up your new package:
https://github.com/napari/napari-plugin-template#getting-started

and review the napari docs for plugin developers:
https://napari.org/stable/plugins/index.html
-->

## Recommended Setup

It is recommended to work within a virtual environment to manage dependencies and avoid conflicts. You can create a virtual environment using `venv`:

```bash
python -m venv myenv
source myenv/bin/activate  # On Windows use `myenv\Scripts\activate`
```

Then, install the required packages within the virtual environment.

## Python Version

This plugin requires Python 3.7 to 3.12. Ensure you have the correct version installed:

```bash
python --version
```

## Installation

This plugin uses the `cupy` library for accelerated GPU/CPU computations. You need to install `cupy` manually based on your hardware configuration:
Refer to the [CuPy installation guide](https://docs.cupy.dev/en/stable/install.html) for detailed instructions.

This plugin requires `napari` and `mbipy`. You need to clone and install `mbipy` with `pip`:

```bash
python -m pip install "napari[all]"
```

```bash
git clone https://github.com/Nin17/mbipy.git
cd mbipy
pip install .
```

To install the latest development version:

```bash
pip install git+https://github.com/Clementcmoi/MoBI_plugin.git
```
## Contributing

Contributions are very welcome. Tests can be run with [tox], please ensure
the coverage at least stays the same before you submit a pull request.

## License

Distributed under the terms of the [MIT] license,
"mobi-plugin" is free and open source software

## Issues

If you encounter any problems, please [file an issue] along with a detailed description.

[napari]: https://github.com/napari/napari
[copier]: https://copier.readthedocs.io/en/stable/
[@napari]: https://github.com/napari
[MIT]: http://opensource.org/licenses/MIT
[BSD-3]: http://opensource.org/licenses/BSD-3-Clause
[GNU GPL v3.0]: http://www.gnu.org/licenses/gpl-3.0.txt
[GNU LGPL v3.0]: http://www.gnu.org/licenses/lgpl-3.0.txt
[Apache Software License 2.0]: http://www.apache.org/licenses/LICENSE-2.0
[Mozilla Public License 2.0]: https://www.mozilla.org/media/MPL/2.0/index.txt
[napari-plugin-template]: https://github.com/napari/napari-plugin-template

[file an issue]: https://github.com/Clementcmoi/mobi-plugin/issues

[napari]: https://github.com/napari/napari
[tox]: https://tox.readthedocs.io/en/latest/
[pip]: https://pypi.org/project/pip/
[PyPI]: https://pypi.org/
````
