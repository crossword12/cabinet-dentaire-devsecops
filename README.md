# Cabinet Dentaire DevSecOps

## 1. Présentation du projet

Ce projet consiste à sécuriser la chaîne de conteneurisation d’une application web de gestion d’un cabinet dentaire.
L’application est développée avec Django et utilise une base de données SQL Server. Elle permet la gestion des patients, des rendez-vous, du catalogue des soins et des profils utilisateurs.

Le projet s’inscrit dans une approche DevSecOps, où la sécurité est intégrée à chaque étape du cycle de développement : code source, image Docker, configuration, pipeline CI/CD et contrôle d’accès applicatif.

---

## 2. Objectifs du projet

Les objectifs principaux sont :

- Conteneuriser une application Django avec Docker.
- Sécuriser la configuration avec des variables d’environnement.
- Scanner le code source avec Bandit.
- Scanner l’image Docker avec Trivy.
- Corriger les vulnérabilités détectées lorsque cela est possible.
- Mettre en place une pipeline DevSecOps avec GitHub Actions.
- Vérifier la séparation des rôles applicatifs.
- Documenter les risques résiduels.

---

## 3. Fonctionnalités de l’application

L’application distingue trois profils métiers :

- **Secrétaire** : gestion des patients, des rendez-vous et du catalogue des soins.
- **Dentiste** : consultation des patients et des rendez-vous.
- **Patient** : consultation de ses propres rendez-vous et du catalogue des soins.

Le superutilisateur Django est réservé à l’administration technique de l’application, notamment la gestion des comptes, des groupes et des permissions.

---

## 4. Technologies utilisées

- Python
- Django
- SQL Server
- Docker
- Docker Compose
- Bandit
- Trivy
- Git
- GitHub
- GitHub Actions

---

## 5. Architecture DevSecOps

La chaîne DevSecOps mise en place suit le processus suivant :

```text
Développement du code Django
        ↓
Analyse statique du code avec Bandit
        ↓
Construction de l’image Docker
        ↓
Analyse de l’image avec Trivy
        ↓
Correction des vulnérabilités détectées
        ↓
Déploiement local avec Docker Compose
        ↓
Surveillance du conteneur avec healthcheck
        ↓
Automatisation avec GitHub Actions
```

---

## 6. Configuration des variables d’environnement

Le fichier `.env` contient les informations sensibles de configuration et n’est pas versionné dans Git.

Un fichier `.env.example` est fourni comme modèle :

```env
SECRET_KEY=change-me
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_HOST=host.docker.internal
DB_PORT=1433

SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False
SECURE_HSTS_SECONDS=0
SECURE_HSTS_INCLUDE_SUBDOMAINS=False
SECURE_HSTS_PRELOAD=False
```

Cette séparation permet de protéger les secrets tout en documentant les variables nécessaires au lancement de l’application.

---

## 7. Lancement avec Docker Compose

Pour construire et lancer l’application :

```bash
docker compose up --build
```

L’application est ensuite accessible à l’adresse :

```text
http://127.0.0.1:8000/
```

Pour arrêter les conteneurs :

```bash
docker compose down
```

Pour vérifier l’état des conteneurs :

```bash
docker ps
```

Le conteneur applicatif dispose d’un healthcheck Docker qui exécute périodiquement :

```bash
python manage.py check
```

Lorsque le service fonctionne correctement, Docker affiche l’état :

```text
healthy
```

---

## 8. Sécurité du code source avec Bandit

Bandit est utilisé pour analyser le code Python/Django et détecter d’éventuelles failles de sécurité.

Commande utilisée :

```bash
bandit -r . -x ./venv
```

Résultat obtenu :

```text
No issues identified.
Total issues: 0
```

Un rapport Bandit est également généré automatiquement dans la pipeline GitHub Actions.

---

## 9. Sécurité de l’image Docker avec Trivy

Trivy est utilisé pour scanner l’image Docker et identifier les vulnérabilités système et applicatives.

Commande utilisée :

```bash
trivy image cabinet-dentaire:1.8
```

Un scan ciblé sur les vulnérabilités importantes a aussi été réalisé :

```bash
trivy image --severity HIGH,CRITICAL cabinet-dentaire:1.8
```

Résultat final :

```text
Python packages : 0 vulnérabilité détectée
Debian packages : vulnérabilités restantes identifiées et documentées
```

Les dépendances Python vulnérables ont été mises à jour, notamment Django et sqlparse. Les outils de développement comme Bandit ont été séparés dans `requirements-dev.txt` afin de ne pas être inclus dans l’image finale.

---

## 10. Pipeline DevSecOps avec GitHub Actions

Une pipeline GitHub Actions a été mise en place afin d’automatiser les contrôles de sécurité à chaque push sur la branche principale.

La pipeline réalise les étapes suivantes :

1. Récupération du code source.
2. Installation des dépendances Python.
3. Scan du code avec Bandit.
4. Construction de l’image Docker.
5. Scan de l’image avec Trivy.
6. Génération des rapports sous forme d’artifacts.

Les artifacts générés sont :

- `bandit-report`
- `trivy-high-critical-report`

---

## 11. Tests d’accès par rôle

Des tests d’accès ont été réalisés afin de vérifier la séparation des rôles.

| Test                      | Compte utilisé | Résultat obtenu                 |
| ------------------------- | -------------- | ------------------------------- |
| Accès `/admin/`           | Superuser      | Autorisé                        |
| Accès `/admin/`           | Secrétaire     | Refusé                          |
| Accès `/patients/`        | Secrétaire     | Autorisé                        |
| Accès `/patients/`        | Patient        | Refusé / redirection            |
| Accès `/soins/catalogue/` | Visiteur       | Autorisé sans actions sensibles |
| Accès `/soins/catalogue/` | Patient        | Autorisé sans actions sensibles |
| Accès `/soins/catalogue/` | Secrétaire     | Autorisé avec actions           |
| Accès `/rendezvous/mes/`  | Patient        | Autorisé                        |
| Accès `/rendezvous/tous/` | Patient        | Refusé / redirection            |
| Accès `/rendezvous/tous/` | Secrétaire     | Autorisé                        |

Ces tests confirment que chaque utilisateur dispose uniquement des accès nécessaires à son rôle.

---

## 12. Durcissement Django

Plusieurs paramètres de sécurité Django ont été activés :

```python
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SECURE_REFERRER_POLICY = "same-origin"

SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"
```

Les paramètres liés à HTTPS sont configurables via les variables d’environnement afin de pouvoir être activés en production.

---

## 13. Risque résiduel

Après correction des dépendances Python, Trivy ne détecte plus de vulnérabilités dans les packages Python de l’application.

Certaines vulnérabilités système Debian restent présentes dans l’image finale. Elles concernent principalement des bibliothèques système fournies par l’image de base. Certaines ne disposent pas encore de correctif disponible ou sont marquées comme non corrigibles par le mainteneur.

Ces vulnérabilités sont considérées comme un risque résiduel identifié, documenté et surveillé régulièrement à travers la pipeline DevSecOps.

---

## 14. Conclusion

Ce projet démontre la mise en place d’une stratégie DevSecOps appliquée à une application web métier.
La sécurité a été intégrée à plusieurs niveaux : code source, configuration, image Docker, dépendances, pipeline CI/CD, contrôle d’accès et surveillance du conteneur.

L’approche mise en œuvre permet de réduire la surface d’attaque, d’automatiser les contrôles de sécurité et de documenter les risques résiduels.
