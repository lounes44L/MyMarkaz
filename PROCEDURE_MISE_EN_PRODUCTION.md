# Procédure de Mise en Production - MyMarkaz

Ce document décrit la procédure complète pour déployer l'application MyMarkaz en production, en tenant compte de la configuration avec Cloudflare D1.

## Prérequis

- Accès SSH au serveur de production
- Compte Cloudflare avec accès à D1
- Python 3.8+ installé
- Node.js et npm pour les assets statiques
- Base de données Cloudflare D1 configurée
- Variables d'environnement de production configurées

## 1. Préparation de l'environnement

### 1.1 Configuration du serveur

```bash
# Mise à jour du système
sudo apt update && sudo apt upgrade -y

# Installation des dépendances système
sudo apt install -y python3-pip python3-venv nginx supervisor

# Configuration du pare-feu
sudo ufw allow 'Nginx Full'
sudo ufw allow 'OpenSSH'
sudo ufw enable
```

### 1.2 Configuration de l'utilisateur et des permissions

```bash
# Création d'un utilisateur dédié
sudo adduser markaz --disabled-password --gecos ""
sudo usermod -aG sudo markaz

# Configuration des permissions
sudo mkdir -p /var/www/mymarkaz
sudo chown -R markaz:markaz /var/www/mymarkaz
```

## 2. Déploiement du code

### 2.1 Récupération du code

```bash
# Se connecter en tant qu'utilisateur markaz
su - markaz

# Cloner le dépôt (ou utiliser votre méthode de déploiement préférée)
git clone https://votre-depot-git.com/mymarkaz.git /var/www/mymarkaz
cd /var/www/mymarkaz

# Créer et activer l'environnement virtuel
python3 -m venv venv
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
pip install -r requirements_production.txt

# Installer les dépendances front-end (si nécessaire)
npm install
```

### 2.2 Configuration de l'application

Créer un fichier `.env` dans le répertoire du projet avec les variables d'environnement nécessaires :

```env
DEBUG=False
SECRET_KEY=votre_secret_key_production
ALLOWED_HOSTS=.votredomaine.com,localhost,127.0.0.1
DATABASE_URL=cloudflare-db-url
DB_NAME=nom-de-votre-base-d1
DB_USER=user-d1
DB_PASSWORD=password-d1
DB_HOST=host-d1
USE_CLOUDFLARE_D1=True
# Autres variables d'environnement spécifiques à la production
```

## 3. Configuration de la base de données

### 3.1 Migration vers Cloudflare D1

```bash
# Activer l'environnement virtuel
source venv/bin/activate

# Appliquer les migrations
python manage.py migrate

# Créer un superutilisateur (si nécessaire)
python manage.py createsuperuser

# Charger les données initiales (si nécessaire)
python manage.py loaddata data_export.json
```

## 4. Configuration de Gunicorn

### 4.1 Installation et configuration

```bash
# Installer Gunicorn
pip install gunicorn

# Créer le fichier de configuration Gunicorn
echo 'command=$(which gunicorn)
workers=5
user=markaz
bind=unix:/run/gunicorn.sock
pythonpath=/var/www/mymarkaz
chdir=/var/www/mymarkaz
module=gestion_markaz.wsgi:application
log-level=error
access-logfile=/var/log/gunicorn/access.log
error-logfile=/var/log/gunicorn/error.log
' | sudo tee /etc/gunicorn.d/gunicorn.py

# Créer le répertoire de logs
sudo mkdir -p /var/log/gunicorn
sudo chown -R markaz:markaz /var/log/gunicorn
```

### 4.2 Configuration de Systemd pour Gunicorn

```bash
# Créer le service systemd
echo '[Unit]
Description=gunicorn daemon
After=network.target

[Service]
User=markaz
Group=www-data
WorkingDirectory=/var/www/mymarkaz
ExecStart=/var/www/mymarkaz/venv/bin/gunicorn --config /etc/gunicorn.d/gunicorn.py gestion_markaz.wsgi:application

[Install]
WantedBy=multi-user.target' | sudo tee /etc/systemd/system/gunicorn.service

# Démarrer et activer le service
sudo systemctl start gunicorn
sudo systemctl enable gunicorn
```

## 5. Configuration de Nginx

### 5.1 Installation et configuration de base

```bash
# Créer le fichier de configuration Nginx
echo 'server {
    listen 80;
    server_name votredomaine.com www.votredomaine.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /var/www/mymarkaz;
    }

    location /media/ {
        root /var/www/mymarkaz;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/run/gunicorn.sock;
    }
}' | sudo tee /etc/nginx/sites-available/mymarkaz

# Activer le site
sudo ln -s /etc/nginx/sites-available/mymarkaz /etc/nginx/sites-enabled
sudo nginx -t  # Tester la configuration
sudo systemctl restart nginx
```

## 6. Configuration de SSL avec Let's Encrypt

```bash
# Installer Certbot
sudo apt install -y certbot python3-certbot-nginx

# Obtenir un certificat SSL
sudo certbot --nginx -d votredomaine.com -d www.votredomaine.com

# Configurer le renouvellement automatique
echo "0 0,12 * * * root python3 -c 'import random; import time; time.sleep(random.random() * 3600)' && certbot renew -q" | sudo tee -a /etc/crontab > /dev/null
```

## 7. Finalisation du déploiement

### 7.1 Collecte des fichiers statiques

```bash
# Se placer dans le répertoire du projet
cd /var/www/mymarkaz

# Activer l'environnement virtuel
source venv/bin/activate

# Collecter les fichiers statiques
python manage.py collectstatic --noinput
```

### 7.2 Redémarrage des services

```bash
sudo systemctl daemon-reload
sudo systemctl restart gunicorn
sudo systemctl restart nginx
```

## 8. Vérification du déploiement

1. Vérifier que le site est accessible via HTTPS
2. Vérifier que les URLs d'administration sont sécurisées
3. Tester l'upload et le téléchargement de fichiers
4. Vérifier la connexion à la base de données Cloudflare D1
5. Vérifier les logs en cas d'erreur :
   ```bash
   sudo journalctl -u gunicorn
   sudo tail -f /var/log/nginx/error.log
   ```

## 9. Maintenance et surveillance

### 9.1 Mises à jour

```bash
# Mettre à jour le code
git pull origin main

# Mettre à jour les dépendances
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements_production.txt

# Appliquer les migrations
python manage.py migrate

# Redémarrer les services
sudo systemctl restart gunicorn
```

### 9.2 Sauvegardes

Mettre en place des sauvegardes régulières de :
- La base de données Cloudflare D1 (via l'interface Cloudflare)
- Les fichiers média
- Le fichier .env contenant les secrets

## 10. Dépannage

### Problèmes courants

1. **Erreurs 502 Bad Gateway**
   - Vérifier que Gunicorn est en cours d'exécution : `sudo systemctl status gunicorn`
   - Vérifier les logs : `sudo journalctl -u gunicorn`

2. **Erreurs de base de données**
   - Vérifier la connexion à Cloudflare D1
   - Vérifier les variables d'environnement
   - Vérifier les logs d'erreur de l'application

3. **Problèmes de permissions**
   - Vérifier les permissions des fichiers et répertoires
   - Vérifier que l'utilisateur `markaz` a les droits nécessaires

## 11. Rétrograder en cas de problème

Si nécessaire, pour revenir à une version précédente :

```bash
# Se placer dans le répertoire du projet
cd /var/www/mymarkaz

# Revenir à un commit spécifique
git checkout <commit-hash>

# Appliquer les migrations si nécessaire
source venv/bin/activate
python manage.py migrate

# Redémarrer les services
sudo systemctl restart gunicorn
```
---
*Dernière mise à jour : 06/09/2024*
