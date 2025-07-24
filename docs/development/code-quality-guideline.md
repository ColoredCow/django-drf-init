### Development Practices

We follow clean, consistent, and maintainable development practices using modern Python and Django REST Framework (DRF) standards. Please review and adhere to the following guidelines.

---

##### 🔧 Code Style & Formatting

We use the following tools to enforce consistent code style:

- **[Black](https://github.com/psf/black)** – Automatic code formatter.
- **[isort](https://github.com/PyCQA/isort)** – Sorts imports according to Black's style.
- **[flake8](https://flake8.pycqa.org/)** – Linting for code quality issues.

> These tools are run automatically via pre-commit hooks before code is committed.

---

##### 🧠 Static Typing

We use **[mypy](https://github.com/python/mypy)** for static type checking.

- Type annotations are required for public functions and classes.
- We use `django-stubs` and `djangorestframework-stubs` to improve type support in Django and DRF.
- Configuration is in `pyproject.toml` or `mypy.ini`.

---

#### 🛡️ Security Checks

We run **[Bandit](https://bandit.readthedocs.io/)** to catch common security issues in Python code, such as unsafe `eval()` usage, hardcoded passwords, etc.

---

#### 🔍 Pre-commit Hooks

Pre-commit hooks are configured in `.pre-commit-config.yaml`. They run checks automatically before any commit.

To install:
```bash
pre-commit install
```
---

#### 💡 Developer Notes

- Use type hints consistently for clarity and safety.
- Avoid `print()` or `pdb.set_trace()` in committed code.
- Keep commits focused and atomic.
- Write docstrings for public modules, classes, and methods.
- Use `.env` and `django-environ` for environment variables.
- Respect `.gitignore` and avoid committing unnecessary files.

----

#### 📄 References

- [Django REST Framework](https://www.django-rest-framework.org/)
- [Black – Code Formatter](https://black.readthedocs.io/)
- [flake8 – Python Linter](https://flake8.pycqa.org/)
- [isort – Import Sorter](https://pycqa.github.io/isort/)
- [mypy – Static Type Checker](https://mypy.readthedocs.io/)
- [Bandit – Security Scanner](https://bandit.readthedocs.io/)
- [Pre-commit Framework](https://pre-commit.com/)
- [pytest](https://docs.pytest.org/)
