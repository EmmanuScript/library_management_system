# Library Management System

An application that manages a library. Handles borrwing of books by user, registration, and returning books. It works with both a user and an admin side on different apps.

## Table of Contents

- [API Endpoints](#api-endpoints)
  - [Frontend API Endpoints (User-Side)](#frontend-api-endpoints-user-facing)
  - [Backend/Admin API Endpoints (Admin-Side)](#backendadmin-api-endpoints-admin-facing)

---

# API Endpoints

## Frontend API Endpoints (User-Side)

Port:8001

| HTTP Method | Endpoint                          | Description                                                                        |
| ----------- | --------------------------------- | ---------------------------------------------------------------------------------- |
| `POST`    | `/api/users/register`           | Register a new user into the library using their email, first name, and last name. |
| `GET`     | `/api/books`                    | Get the list of all available books in the library.                               |
| `GET`     | `/api/books/{id}`               | Get Data of a single book by its ID.                                               |
| `GET`     | `/api/books?publisher={name}`   | Filter books by publisher (e.g., Wiley, Apress, Manning).                          |
| `GET`     | `/api/v1/books?category={name}` | Filter books by category (e.g., fiction, technology, science).                     |
| `POST`    | `/api/books/borrow_books/{id}`  | Borrow a book by its ID, specifying how many days the user wants to borrow it for. |

## Backend/Admin API Endpoints (Admin-Facing)

Port 8000

| HTTP Method | Endpoint                      | Description                                                                            |
| ----------- | ----------------------------- | -------------------------------------------------------------------------------------- |
| `POST`    | `/api/books`                | Add a new book to the catalog.                                                         |
| `DELETE`  | `/api/books/{id}`           | Remove a book from the catalog by its ID.                                              |
| `GET`     | `/api/users`                | Fetch a list of all users enrolled in the library.                                     |
| `GET`     | `/api/users/borrowed-books` | Fetch a list of users and the books they have borrowed.                                |
| `GET`     | `/api/books/unavailable`    | List books that are not available for borrowing and when they will be available again. |
