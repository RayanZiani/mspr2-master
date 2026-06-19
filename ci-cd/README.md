# 🚀 CI/CD FutureKawa - Guide Complet

## 📋 Vue d'ensemble

Ce projet utilise une stack CI/CD complète :
- **Jenkins** : Pipeline de build, tests et déploiement
- **SonarQube** : Analyse qualité du code
- **GitHub Actions** : Déploiement automatique sur Render
- **Render** : Hébergement production

---

## 🏗️ Architecture CI/CD

```
GitHub Push → Jenkins Pipeline → Tests → SonarQube → Déploiement Render
              ↓                    ↓         ↓              ↓
           Build Images      Unit/Int/E2E  Quality   Backend + Frontend
                                           Gate          (Production)
```

---

## 🔧 Configuration Jenkins

### 1. Démarrer Jenkins localement

```bash
# Depuis la racine du projet
cd ci-cd/jenkins

# Build l'image Jenkins personnalisée
docker build -t futurekawa-jenkins .

# Lancer Jenkins
docker run -d \
  -p 8080:8080 \
  -p 50000:50000 \
  -v jenkins_home:/var/jenkins_home \
  -v /var/run/docker.sock:/var/run/docker.sock \
  --name jenkins \
  futurekawa-jenkins
```

### 2. Accéder à Jenkins

- **URL** : http://localhost:8080
- **Mot de passe initial** :
  ```bash
  docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
  ```

### 3. Configuration initiale

1. Installer les plugins recommandés
2. Créer un compte admin
3. Configurer l'URL de Jenkins : `http://localhost:8080`

### 4. Créer le pipeline

1. **New Item** → **Pipeline** → Nom : `FutureKawa-CI-CD`
2. **Pipeline** section :
   - **Definition** : Pipeline script from SCM
   - **SCM** : Git
   - **Repository URL** : `https://github.com/RayanZiani/mspr2-master`
   - **Branch** : `*/feature/ci-cd-jenkins` ou `*/main`
   - **Script Path** : `ci-cd/Jenkinsfile`

### 5. Configurer les credentials Jenkins

Allez dans **Manage Jenkins** → **Credentials** → **System** → **Global credentials** :

#### a. Docker Hub (optionnel)
- **Kind** : Secret text
- **ID** : `dockerhub-credentials`
- **Secret** : Votre token Docker Hub

#### b. Render Backend Deploy Hook
- **Kind** : Secret text
- **ID** : `render-backend-deploy-hook`
- **Secret** : URL du Deploy Hook backend Render
  - Ex: `https://api.render.com/deploy/srv-xxxxx?key=yyyyy`

#### c. Render Frontend Deploy Hook
- **Kind** : Secret text
- **ID** : `render-frontend-deploy-hook`
- **Secret** : URL du Deploy Hook frontend Render

---

## 🔍 Configuration SonarQube

### 1. Démarrer SonarQube localement

```bash
docker run -d \
  -p 9000:9000 \
  -e SONAR_ES_BOOTSTRAP_CHECKS_DISABLE=true \
  --name sonarqube \
  sonarqube:lts-community
```

### 2. Accéder à SonarQube

- **URL** : http://localhost:9000
- **Credentials par défaut** :
  - Username : `admin`
  - Password : `admin` (changez-le au premier login)

### 3. Créer un projet

1. **Projects** → **Create Project** → **Manually**
2. **Project key** : `futurekawa`
3. **Project name** : `FutureKawa IoT`

### 4. Générer un token

1. **My Account** → **Security** → **Generate Token**
2. **Name** : `Jenkins`
3. **Type** : Global Analysis Token
4. Copiez le token généré

### 5. Configurer Jenkins pour SonarQube

Dans Jenkins :
1. **Manage Jenkins** → **System**
2. **SonarQube servers** → **Add SonarQube**
   - **Name** : `SonarQube`
   - **Server URL** : `http://host.docker.internal:9000` (ou votre IP)
   - **Server authentication token** : Ajoutez un credential Secret text avec votre token SonarQube

---

## 🌐 Déploiement Render

### URLs de production

| Service | URL |
|---------|-----|
| **Backend API** | https://mspr2-master.onrender.com |
| **Frontend** | https://mspr2-master-front.onrender.com |
| **Health Check** | https://mspr2-master.onrender.com/health |
| **API Docs** | https://mspr2-master.onrender.com/docs |

### GitHub Actions (automatique)

Le workflow `.github/workflows/deploy-render.yml` se déclenche automatiquement :
- ✅ À chaque push sur `feature/ci-cd-jenkins` ou `main`
- ✅ Détection intelligente des changements
- ✅ Déploiement sélectif (backend/frontend/les deux)

### Jenkins (manuel ou déclenché par webhook)

Le stage "Déploiement Render" dans le Jenkinsfile déclenche les déploiements :
- ✅ Après succès des tests
- ✅ Sur les branches `main` et `feature/ci-cd-jenkins`
- ✅ Utilise les Deploy Hooks Render

---

## 🧪 Tests disponibles

Le pipeline Jenkins exécute :

| Type | Description | Commande |
|------|-------------|----------|
| **Lint** | Flake8 sur le code Python | `flake8 ...` |
| **Unitaires** | Tests pytest unitaires | `pytest tests/unit/` |
| **Intégration** | Tests d'intégration API | `pytest tests/integration/` |
| **API** | Tests Newman/Postman | `newman run ...` |
| **E2E** | Tests Playwright | `playwright test` |

---

## 📊 Rapports générés

### Jenkins
- **JUnit** : Résultats des tests XML
- **Coverage** : Rapport HTML de couverture
- **Artifacts** : Tous les rapports dans `tests/reports/`

### SonarQube
- **Code Smells** : Problèmes de qualité
- **Bugs** : Bugs potentiels détectés
- **Vulnerabilities** : Failles de sécurité
- **Coverage** : Couverture de code
- **Duplications** : Code dupliqué

---

## 🔄 Workflow complet

### 1. Développement local
```bash
git checkout -b feature/ma-feature
# ... développement ...
git add .
git commit -m "feat: ma nouvelle fonctionnalité"
git push -u origin feature/ma-feature
```

### 2. Déclenchement automatique
- ✅ GitHub Actions démarre (si configuré)
- ✅ Jenkins pipeline démarre (si webhook configuré)

### 3. Exécution des tests
1. Build des images Docker
2. Démarrage de la stack complète
3. Tests unitaires
4. Analyse statique (SonarQube)
5. Tests d'intégration
6. Tests API
7. Tests E2E

### 4. Quality Gate
- SonarQube vérifie les critères de qualité
- Le pipeline peut continuer ou échouer selon les résultats

### 5. Déploiement (si branche main)
- Images poussées vers Docker Hub (optionnel)
- Déploiement automatique sur Render
- Backend et Frontend mis à jour

---

## 🚨 Dépannage

### Jenkins ne trouve pas Docker

```bash
# Vérifier que le socket Docker est monté
docker inspect jenkins | grep docker.sock
```

### SonarQube non accessible depuis Jenkins

Utilisez `host.docker.internal` au lieu de `localhost` dans la configuration Jenkins.

### Tests échouent dans Jenkins

```bash
# Vérifier les logs des conteneurs
docker-compose logs

# Exécuter les tests localement
bash ci-cd/scripts/run_tests.sh unit
```

### Déploiement Render échoue

1. Vérifier que les Deploy Hooks sont corrects dans Jenkins Credentials
2. Vérifier les logs sur Render Dashboard
3. Vérifier que les variables d'environnement sont configurées sur Render

---

## 📈 Monitoring

### UptimeRobot (recommandé)

Configurez des monitors pour :
- ✅ Backend : `https://mspr2-master.onrender.com/health` (5 min)
- ✅ Frontend : `https://mspr2-master-front.onrender.com` (5 min)

Cela empêche les services Render gratuits de s'endormir.

---

## 🔐 Sécurité

- ❌ Ne jamais commit les credentials
- ✅ Utiliser les secrets Jenkins/GitHub
- ✅ Variables d'environnement sur Render
- ✅ Deploy Hooks protégés par des tokens

---

## 📚 Ressources

- [Documentation Jenkins](https://www.jenkins.io/doc/)
- [Documentation SonarQube](https://docs.sonarqube.org/)
- [Documentation Render](https://render.com/docs)
- [GitHub Actions](https://docs.github.com/en/actions)

---

## ✅ Checklist de mise en production

- [ ] Jenkins configuré et accessible
- [ ] SonarQube configuré et accessible
- [ ] Pipeline Jenkins créé et testé
- [ ] Credentials Jenkins configurés
- [ ] GitHub Actions configuré
- [ ] Services Render déployés et opérationnels
- [ ] Variables d'environnement Render configurées
- [ ] UptimeRobot configuré
- [ ] Tests passent en local et dans Jenkins
- [ ] Quality Gate SonarQube validée
- [ ] Documentation à jour

---

**Auteurs** : Équipe FutureKawa  
**Dernière mise à jour** : 16 juin 2026
