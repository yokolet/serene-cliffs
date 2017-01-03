# Book catalog

This directory has code for Book catalog web app.
Once Vagrant virtual machine is up and running, the app will run
with setups.

## How to run the app

The app uses PostgreSQL. The databse `catalog` should be created
on PostgreSQL.

```
$ psql
vagrant=> create database catalog;
```

Then create schema and transact seed data.

```
$ python database_setup.py
$ python seeds.py
```

Now, the web app is ready to run. Start the web app by:

```
$ python project.py
```


If the app starts, open `http://localhost:5000/` on the browser.


## Facebook account

This app uses Facebook OAuth for a user login. To use app's
create/edit/delete feature, be ready to use the Facebook account.


## API endpoints

This app supports four types of API endpoints by JSON.

1. shows all books

    example

    ```
    http://localhost:5000/book_catalog/books/JSON
    ```

2. shows all categories

    example

    ```
    http://localhost:5000/book_catalog/categories/JSON
    ```

3. shows all books of a specified category id

    example

    ```
    http://localhost:5000/book_catalog/categories/1/books/JSON
    ```

4. shows a book of a specified book id

    example

    ```
    http://localhost:5000/book_catalog/books/1/JSON
    ```