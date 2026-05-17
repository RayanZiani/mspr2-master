# FutureKawa

Plateforme IoT de surveillance des stocks de café vert (Brésil, Équateur, Colombie + siège).

## Démarrage (une seule commande)

Prérequis : [Docker Desktop](https://www.docker.com/products/docker-desktop/) démarré.

```powershell
npm start
```

Équivalent :

```powershell
.\start.ps1
```

En arrière-plan : `npm run start:detached` ou `.\start.ps1 -Detached`

- **Interface web** : http://localhost
- **API siège (Swagger)** : http://localhost/api/docs
- **Arrêt** : `npm run stop`
