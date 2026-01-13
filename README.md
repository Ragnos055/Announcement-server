# Announcement-server

Petit tracker TCP pour partager la liste des pairs du client lourd Decentralis.
Il gère deux actions JSON simples :

- `announce` : enregistre/rafraîchit un pair et renvoie un UUID
- `getpeers` : retourne la liste des pairs connus (hors requérant)

Les pairs inactifs sont nettoyés automatiquement toutes les 30 s.

## Prérequis

- Python 3.10+ (3.11 conseillé)
- Port ouvert (par défaut `5000`)

## Lancer en local

```bash
cd src/decentralis-announcement-server
python main.py
```

Le tracker écoute sur `0.0.0.0:<PORT>`.

## Docker

```bash
docker build -t decentralis-announcement .
docker run -p 5000:5000 -e PORT=5000 decentralis-announcement
```

## Docker Compose

```bash
PORT=5000 docker compose up -d
```

## API minimale

- `announce`
  - Requête : `{"action":"announce","ip":"1.2.3.4","port":4000,"uuid":"facultatif"}`
  - Réponse : `{"status":"ok","uuid":"<attribué>"}`. Si `uuid` fourni existe déjà, il est réutilisé.

- `getpeers`
  - Requête : `{"action":"getpeers","uuid":"<votre_uuid>"}` (UUID facultatif)
  - Réponse : `{"peers":["ip:port","ip:port", ...]}` sans inclure le requérant.

## Utilisation avec le client lourd

1. Démarrez le tracker (local ou sur un serveur accessible).
2. Lancez le client lourd : `python .\src\decentralis-client\main.py` dans le dépôt
   [`Client-lourd`](https://github.com/Ragnos055/Client-lourd).
3. Dans l’en-tête de l’application :
   - saisissez l’IP du tracker et le port (ex. `http://<ip>:5000` n’est pas requis : indiquez seulement l’IP et le port),
   - indiquez votre IP et port de pair locaux,
   - cliquez sur `Connexion`.
4. La vue `Pairs` se rafraîchit toutes les ~2 s et affiche les pairs annoncés par le tracker.

## Notes

- Délai d’expiration pair : 30 s sans annonce -> suppression du peer.
- Le protocole est volontairement minimaliste pour faciliter l’intégration côté
  client lourd ; aucune persistance sur disque.
