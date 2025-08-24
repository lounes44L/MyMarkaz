# Script to specifically fix the urls.py file
with open('ecole_app/urls.py.clean', 'rb') as f:
    clean_content = f.read()

with open('ecole_app/urls.py', 'wb') as f:
    f.write(clean_content)

print("urls.py has been replaced with the clean version.")
