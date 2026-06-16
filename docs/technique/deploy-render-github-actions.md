# 🚀 Configuration GitHub Actions pour Render

Ce guide explique comment configurer les déploiements automatiques vers Render via GitHub Actions.

## 📋 Prérequis

1. Services Render créés (backend + frontend)
2. Accès aux paramètres GitHub du repository

---

## 🔐 Étape 1 : Obtenir les Deploy Hooks de Render

### Pour le Backend

1. Allez sur [Render Dashboard](https://dashboard.render.com)
2. Sélectionnez votre service **Backend** (API)
3. Allez dans **Settings**
4. Cherchez la section **Deploy Hook**
5. Copiez l'URL (format : `https://api.render.com/deploy/srv-xxxxx?key=yyyyy`)

### Pour le Frontend

1. Sélectionnez votre service **Frontend**
2. Répétez les mêmes étapes
3. Copiez l'URL du Deploy Hook

---

## 🔑 Étape 2 : Configurer les Secrets GitHub

1. Allez sur votre repo GitHub : `https://github.com/RayanZiani/mspr2-master`
2. Cliquez sur **Settings** (dans le repo)
3. Allez dans **Secrets and variables** → **Actions**
4. Cliquez sur **New repository secret**
5. Ajoutez ces deux secrets :

### Secret 1 : RENDER_BACKEND_DEPLOY_HOOK

- **Name** : `RENDER_BACKEND_DEPLOY_HOOK`
- **Value** : URL du Deploy Hook du backend (copiée précédemment)

### Secret 2 : RENDER_FRONTEND_DEPLOY_HOOK

- **Name** : `RENDER_FRONTEND_DEPLOY_HOOK`
- **Value** : URL du Deploy Hook du frontend (copiée précédemment)

---

## ✅ Étape 3 : Tester le workflow

Une fois les secrets configurés, le workflow se déclenchera automatiquement :

### Déclenchement automatique
- ✅ À chaque `push` sur `feature/ci-cd-jenkins`
- ✅ À chaque `push` sur `main`
- ✅ Détecte automatiquement les changements backend ou frontend

### Déclenchement manuel
1. Allez dans l'onglet **Actions** du repo
2. Sélectionnez **Deploy to Render**
3. Cliquez sur **Run workflow**

---

## 🎯 Comment ça fonctionne

### Détection intelligente des changements

Le workflow détecte automatiquement quels services ont changé :

| Dossier modifié | Action |
|----------------|--------|
| `siege/api/**` | ✅ Déploie le backend uniquement |
| `siege/frontend/**` | ✅ Déploie le frontend uniquement |
| Les deux | ✅ Déploie backend + frontend |
| Autre dossier | ⏭️ Aucun déploiement |

### Exemple de logs

```
📦 Résumé du déploiement
✅ Backend : Déployé
⏭️ Frontend : Aucun changement
```

---

## 🔧 Vérification

Pour vérifier que tout fonctionne :

1. Modifiez un fichier dans `siege/api/` ou `siege/frontend/`
2. Commitez et pushez
3. Allez dans l'onglet **Actions** de GitHub
4. Vous verrez le workflow se lancer automatiquement
5. Les services Render se déploieront automatiquement

---

## 📊 Services déployés

| Service | URL | Status |
|---------|-----|--------|
| Backend API | https://mspr2-master.onrender.com | ✅ |
| Frontend | https://mspr2-frontend.onrender.com | 🔄 À configurer |

---

## 🆘 Dépannage

### Le workflow ne se déclenche pas
- Vérifiez que les secrets sont bien configurés dans GitHub
- Vérifiez que vous pushez sur la bonne branche (`feature/ci-cd-jenkins` ou `main`)

### Le déploiement échoue
- Vérifiez que les URLs des Deploy Hooks sont correctes
- Vérifiez que les services Render sont bien créés et actifs
- Consultez les logs dans l'onglet Actions de GitHub

### Comment désactiver le déploiement automatique
Supprimez ou renommez le fichier `.github/workflows/deploy-render.yml`

---

## 📚 Ressources

- [Documentation Render Deploy Hooks](https://render.com/docs/deploy-hooks)
- [Documentation GitHub Actions](https://docs.github.com/en/actions)
- [Documentation dorny/paths-filter](https://github.com/dorny/paths-filter)
