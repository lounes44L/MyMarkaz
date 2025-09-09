# Configuration temporaire pour la migration D1
import os

# Configuration Cloudflare D1
os.environ['CLOUDFLARE_ACCOUNT_ID'] = '16ae7ea2603e2ae54786ffeaa02ab521'
os.environ['CLOUDFLARE_DATABASE_ID'] = 'ceb7a18d-a912-4db5-955e-94bdaad8f18c'
os.environ['CLOUDFLARE_API_TOKEN'] = 'jIWsnvouzsE_hmIOvB0iOcKCjAxvtupD0EFIF6Q8'
os.environ['USE_CLOUDFLARE_D1'] = 'False'  # Sera activé après migration
os.environ['SECRET_KEY'] = 'django-insecure-3k4ad-xui)q4+z$q33rbg(b3qp%kom&sbhay6)i(3!g=+3z(ce'
os.environ['DEBUG'] = 'True'

print("Configuration D1 chargée !")
