import httpx
import asyncio
import random

BASE_URL = "http://127.0.0.1:8000"

# Evenements possibles du Order Service
ORDER_EVENTS = [
    {
        "event_type": "order.created",
        "source_service": "order",
        "payload": {"order_id": "ORD-001", "amount": 49.99, "customer_id": "CUST-123"},
    },
    {
        "event_type": "order.cancelled",
        "source_service": "order",
        "payload": {"order_id": "ORD-002", "reason": "customer_request", "customer_id": "CUST-456"},
    },
]

# Evenements possibles du Payment Service
PAYMENT_EVENTS = [
    {
        "event_type": "payment.validated",
        "source_service": "payment",
        "payload": {"order_id": "ORD-001", "amount": 49.99, "method": "mobile_money"},
    },
    {
        "event_type": "payment.failed",
        "source_service": "payment",
        "payload": {"order_id": "ORD-003", "reason": "insufficient_funds", "amount": 99.99},
    },
]


async def send_event(client: httpx.AsyncClient, event: dict, service_name: str):
    """Envoie un evenement a l'Event Manager."""
    try:
        response = await client.post(f"{BASE_URL}/events", json=event)
        if response.status_code == 201:
            data = response.json()
            print(f"[{service_name}] Evenement envoye : {event['event_type']} | id: {data['id']}")
        else:
            print(f"[{service_name}] Erreur {response.status_code} : {response.text}")
    except Exception as e:
        print(f"[{service_name}] Erreur de connexion : {e}")


async def simulate_order_service(client: httpx.AsyncClient):
    """Simule le Order Service."""
    for event in ORDER_EVENTS:
        await send_event(client, event, "OrderService")
        await asyncio.sleep(1)


async def simulate_payment_service(client: httpx.AsyncClient):
    """Simule le Payment Service."""
    for event in PAYMENT_EVENTS:
        await send_event(client, event, "PaymentService")
        await asyncio.sleep(1)


async def main():
    print("Demarrage du simulateur...")
    print(f"Cible : {BASE_URL}")
    print("-" * 40)

    async with httpx.AsyncClient() as client:
        # Les deux services emettent en parallele
        await asyncio.gather(
            simulate_order_service(client),
            simulate_payment_service(client),
        )

    print("-" * 40)
    print("Simulation terminee. Verificez GET /events et GET /metrics.")


if __name__ == "__main__":
    asyncio.run(main())