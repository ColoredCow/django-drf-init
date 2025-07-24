## Installation

**Prerequisites**
   Make sure you have installed all [prerequisites](./pre-requisites.md) before using the installation guide.

**Installation steps**
1. Clone this repository and move to the `<<repo-name>>` directory
   ```sh
   git clone https://github.com/coloredcow-admin/<<repo-name>>.git

   cd <<repo-name>>
   ```

1. Create python environment
   ```sh
   python -m venv venv
   ```

1. Activate the environment
   - For macOS and Linux:
      ```sh
      source venv/bin/activate
      ```
   - For Windows:
      ```sh
      venv/scripts/activate
      ```

1. Install dependencies

   **🔧 For Development Environment**

   Install all necessary packages including development tools (e.g., linters, test runners):
   ```sh
   pip install -r requirements/dev.txt
   ```

   **🚀 For Staging/Production Environment**

   Install only the core dependencies required to run the application:
   ```sh
   pip install -r requirements/base.txt
   ```

   **➕ Adding New Dependencies**
   1. Determine the target environment:
      1. If the dependency is needed in production (e.g., Django, gunicorn), add it to `requirements/base.txt`.
      2. If the dependency is only used for development (e.g., pytest, black, pre-commit), add it to `requirements/dev.txt`.

   2. Lock the current version in targeted environment requirement file
       ```shell
       pip freeze > requirements/dev.txt # for dev dependencies

       pip freeze > requirements/base.txt # for production dependencies
       ```

1. Setup `.env` configuration
   1. Copy and edit `.env`
      ```sh
      cp .env.example .env
      ```
   1. Generate a `SECRET_KEY`
      ```sh
      python -c "import secrets; print(secrets.token_urlsafe(50))"
      ```
      Copy the output and paste it into your `.env` like:
      ```
      SECRET_KEY=your_generated_key_here
      ```

1. Set Up PostgreSQL
   1. Check port **5432** is free
      ```sh
      lsof -i :5432
      ```

   1. Create role and database
      ```sh
      psql postgres
      ```
      Then run:
      ```sql
      CREATE ROLE postgres WITH LOGIN SUPERUSER PASSWORD 'postgres';
      CREATE DATABASE <<databse-name>>;
      \q
      ```

1. Run migrations
   ```sh
   python manage.py migrate
   ```

1. Run the development server
   ```sh
   python manage.py runserver
   ```

1. When the server starts, access the app at: [http://127.0.0.1:8000/](http://127.0.0.1:8000/).
