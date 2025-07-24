**`docs/development/release.md`**
```markdown
# Release

We aim to document any modifications targeted to be released on production as a Github release. These modifications includes bug fixes, hot fixes, routine releases, and more.

### Prerequisites
- The code has been tested locally and on staging and is ready for release on production.
- All changes (new feature and bug fixes) should be ready to be documented as a part of `Release Notes`.
- If this release includes any breaking changes, they are clearly indicated under `BREAKING CHANGES` section in the `Release Notes`.

### Versioning
We are utilizing __Semantic Versioning__ for our release process. For more details, please visit [http://semver.org/](http://semver.org/).

```js
Given a version number MAJOR.MINOR.PATCH, increment the:
1. MAJOR version when you make incompatible code changes
2. MINOR version when you add functionality in a backward compatible manner
3. PATCH version when you make backward compatible bug fixes

Additional labels for pre-release and build metadata are available as extensions to the MAJOR.MINOR.PATCH format.
