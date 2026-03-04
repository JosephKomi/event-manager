import httpx
import asyncio
import json
from datetime import datetime, timezone

BASE_URL = "http://127.0.0.1:8000"
LOG_FILE = "notifications.log"
POLL_INTERVAL = 5  # secondes entre chaque verification


def write_log(message: str):
    """Ecrit un message dans le fichier de log et dans la console."""
    timestamp = datetime.now(timezone.utc).isoformat()
    log_line = f"[{timestamp}] {message}"
    print(log_line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_line + "\n")


async def fetch_pending_events(client: httpx.AsyncClient) -> list:
    """Recupere tous les evenements au statut PENDING."""
    try:
        response = await client.get(
            f"{BASE_URL}/events",
            params={"status": "PENDING", "limit": 100}
        )
        if response.status_code == 200:
            return response.json()
        else:
            write_log(f"Erreur lors de la recuperation des evenements : {response.status_code}")
            return []
    except Exception as e:
        write_log(f"Erreur de connexion : {e}")
        return []


async def update_event_status(client: httpx.AsyncClient, event_id: str, status: str):
    """Met a jour le statut d'un evenement."""
    try:
        await client.patch(
            f"{BASE_URL}/events/{event_id}/status",
            json={"status": status}
        )
    except Exception as e:
        write_log(f"Erreur mise a jour statut {event_id} : {e}")


async def process_event(client: httpx.AsyncClient, event: dict):
    """Traite un evenement PENDING."""
    event_id = event["id"]
    event_type = event["event_type"]
    source_service = event["source_service"]
    payload = json.loads(event["payload"])

    # Simulation du traitement selon le type d'evenement
    if event_type == "order.created":
        message = f"NOTIFICATION : Nouvelle commande recue | order_id={payload.get('order_id')} | montant={payload.get('amount')}"
    elif event_type == "order.cancelled":
        message = f"NOTIFICATION : Commande annulee | order_id={payload.get('order_id')} | raison={payload.get('reason')}"
    elif event_type == "payment.validated":
        message = f"NOTIFICATION : Paiement valide | order_id={payload.get('order_id')} | montant={payload.get('amount')}"
    elif event_type == "payment.failed":
        message = f"NOTIFICATION : Paiement echoue | order_id={payload.get('order_id')} | raison={payload.get('reason')}"
    else:
        message = f"NOTIFICATION : Evenement inconnu | type={event_type} | service={source_service}"

    write_log(message)
    await update_event_status(client, event_id, "PROCESSED")


async def main():
    write_log("Notification Service demarre")
    write_log(f"Verification toutes les {POLL_INTERVAL} secondes")
    write_log("-" * 50)

    async with httpx.AsyncClient() as client:
        while True:
            events = await fetch_pending_events(client)

            if events:
                write_log(f"{len(events)} evenement(s) PENDING trouve(s)")
                for event in events:
                    await process_event(client, event)
            else:
                write_log("Aucun evenement PENDING")

            await asyncio.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    asyncio.run(main())