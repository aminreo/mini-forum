# Mini Forum app
backend app using `fastapi` and `sqlite` (in progress)

# Features
* working `/register` and `/login` routes
* password hashing
* username and password validation

# Usage/Testing
0. (optional) setting up `venv`
1. install requirements: `fastapi` and `pwdlib`

2. run using `uvicorn`
```powershell
uvicorn main:app --reload
```
3. then use [Swagger UI docs](http://127.0.0.1:8000/docs) 