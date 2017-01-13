# Book catalog

This directory has code for Book catalog web app.
Once Vagrant virtual machine is up and running, the app will run
with setups.

## How to run the app

The app uses PostgreSQL. The database `catalog` should be created
on PostgreSQL.

```
$ psql
vagrant=> create database catalog;
```

The app uses [Flask-Restless](https://flask-restless.readthedocs.io/en/stable/index.html)
to provide JSON endpoint. The module is not installed by default.
Install the module before runs the app.

```
sudo pip install Flask-Restless
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
JSON enpoints support HTTP GET method only.

1. shows all books, categories or users

    ```
    http://localhost:5000/api/book
    http://localhost:5000/api/category
    http://localhost:5000/api/book_user
    ```

2. shows one book, cateogory or user

    example:

    ```
    http://localhost:5000/api/book/1
    http://localhost:5000/api/category/1
    http://localhost:5000/api/book_user/1
    ```

3. shows associated records

    example

    ```
    http://localhost:5000/api/cagetory/1/user
    http://localhost:5000/api/book/1/category
    ```

