# E08 Python product

This package is restricted to acceptance in `splrad/steward-e08-product`.
The product has no runtime dependencies. Its wheel and sdist are GitHub
Release assets; publishing to PyPI is outside this acceptance.

`pyproject.toml`, Release Please configuration and the build requirements
lock belong to the exact reviewed source commit S. The native workflow
uses the frozen controller C and verifies the existing release-state/RP
identity before building or accepting assets.

The candidate PR creates `CHANGELOG.md` and `.release-notes/python.md`
before its merged commit becomes source S. Dependency preparation may
download the packages recorded in `requirements-build.txt` from PyPI;
hash verification is required. Distribution building then runs offline,
followed by twine metadata checks.
