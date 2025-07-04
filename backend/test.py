from django.contrib.auth.hashers import make_password

hashed_password = make_password("admin")
print(hashed_password)
