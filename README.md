# Event Manager

Service central de gestion des événements pour une plateforme e-commerce en microservices.

---

## 1. Architecture

La plateforme est organisée en 3 services :
```
+------------------+         POST /events          +-------------------+
|   simulator      | ----------------------------> |   Event Manager   |
| (Order Service + |                               |   (FastAPI)       |
|  Payment Service)|                               |                   |
+------------------+                               |  POST /events     |
                                                   |  GET  /events     |
                                                   |  GET  /events/id  |
                                                   |  GET  /health     |
                                                   |  GET  /metrics    |
                                                   +--------+----------+
                                                            |
                                                       SQLite (events.db)
                                                            |
                                                   +--------+----------+
                                                   | Notification      |
                                                   | Service           |
                                                   | GET /events?      |
                                                   | status=PENDING    |
                                                   +-------------------+
```

### Choix d'architecture

- **Ingestion** : REST HTTP via `POST /events`
- **Souscription** : Pull HTTP (polling toutes les 5 secondes)
- **Base de données** : SQLite avec index sur `status`, `event_type`, `source_service`

Ce choix est cohérent, simple et suffisant pour démontrer l'architecture event-driven.

---

## 2. Stack technique

- Python 3.10
- FastAPI
- SQLite + aiosqlite
- Docker + docker-compose

---

## 3. Lancement du projet

### Prérequis

- Docker Desktop installé
- Git

### Avec Docker (recommandé)
```bash
# Cloner le repository
git clone https://github.com/JosephKomi/event-manager.git
cd event-manager

# Copier le fichier de configuration
copy .env.example .env

# Lancer tous les services
docker-compose up --build
```

Les services démarrent dans cet ordre :
1. `event_manager` démarre sur le port 8000
2. `simulator` envoie les événements de test
3. `notification_service` consomme les événements PENDING

### Sans Docker
```bash
# Créer et activer l'environnement virtuel
python -m venv venv
venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt

# Copier le fichier de configuration
copy .env.example .env

# Terminal 1 : lancer le serveur
uvicorn main:app --reload

# Terminal 2 : lancer le simulateur
python simulator.py

# Terminal 3 : lancer le notification service
python notification_service.py
```

---

## 4. Comment tester

### Documentation interactive

Une fois le serveur lancé, ouvrez :
```
http://127.0.0.1:8000/docs
```

### Exemples curl

#### Envoyer un événement
```bash
curl -X POST http://127.0.0.1:8000/events \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "order.created",
    "source_service": "order",
    "payload": {"order_id": "ORD-001", "amount": 49.99}
  }'
```

#### Lister les événements PENDING
```bash
curl http://127.0.0.1:8000/events?status=PENDING
```

#### Filtrer par type et paginer
```bash
curl "http://127.0.0.1:8000/events?event_type=order.created&page=1&limit=5"
```

#### Détail d'un événement
```bash
curl http://127.0.0.1:8000/events/{id}
```

#### Etat du service
```bash
curl http://127.0.0.1:8000/health
```

#### Statistiques
```bash
curl http://127.0.0.1:8000/metrics
```

---

## 5. Fonctionnement du Notification Service

Le Notification Service utilise le mode **Pull HTTP (polling)** :
```
1. Toutes les 5 secondes :
   GET /events?status=PENDING

2. Pour chaque evenement PENDING :
   - Genere une notification selon le type d'evenement
   - Ecrit dans notifications.log
   - Met a jour le statut : PATCH /events/{id}/status -> PROCESSED

3. Si aucun evenement PENDING :
   - Attend 5 secondes et recommence
```

Les types d'evenements traites :

| event_type | Action |
|---|---|
| order.created | Notification nouvelle commande |
| order.cancelled | Notification commande annulee |
| payment.validated | Notification paiement valide |
| payment.failed | Notification paiement echoue |

---

## 6. Structure du projet
```
event-manager/
│
├── main.py                   # Point d'entree FastAPI
├── database.py               # Connexion SQLite + creation table
├── models.py                 # Schemas Pydantic
├── simulator.py              # Simule Order et Payment Service
├── notification_service.py   # Subscriber Pull HTTP
├── requirements.txt          # Dependances Python
├── Dockerfile                # Image Docker
├── docker-compose.yml        # Orchestration des services
├── .env.example              # Variables d'environnement
├── README.md                 # Documentation
│
└── routes/
    ├── __init__.py
    ├── events.py             # POST /events, GET /events, GET /events/{id}
    └── monitoring.py         # GET /health, GET /metrics
```

---

## 7. Limites connues et améliorations possibles

**Limites actuelles :**
- Le worker de traitement automatique (asyncio) n'est pas implémenté
- Pas de système de retry en cas d'echec de traitement
- SQLite n'est pas adapté à un environnement de production haute charge
- Le Notification Service ne fait qu'écrire dans un fichier log

**Améliorations possibles :**
- Ajouter un worker asyncio pour traiter automatiquement les événements PENDING
- Implémenter un système de retry avec limite configurable
- Migrer vers PostgreSQL pour la production
- Ajouter un système de webhook pour notifier activement les subscribers
- Ajouter des tests unitaires et d'intégration
- Mettre en place un système d'authentification sur les routes