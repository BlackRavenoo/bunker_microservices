from fast_depends.msgspec import MsgSpecSerializer
from faststream.rabbit import RabbitBroker, RabbitExchange, ExchangeType

from services.game_service.app.core.config import settings
from shared.src.consts import GAME_EXCHANGE_NAME
from shared.src.events import GameEvent

class GamePublisher:
    def __init__(self):
        self.exchange = RabbitExchange(
            name=GAME_EXCHANGE_NAME,
            type=ExchangeType.TOPIC,
            durable=True,
        )

        self.broker = RabbitBroker(
            url=settings.rabbitmq_url,
            serializer=MsgSpecSerializer()
        )

    async def start(self):
        await self.broker.start()
        await self.broker.declare_exchange(self.exchange)
    
    async def stop(self):
        await self.broker.stop()

    async def publish(
        self,
        event: GameEvent,
        routing_key: str | None = None
    ):
        if routing_key is None:
            routing_key = event.event_type
        
        await self.broker.publish(
            message=event,
            exchange=self.exchange,
            routing_key=routing_key
        )

_publisher: GamePublisher | None = None

def init_publisher() -> GamePublisher:
    global _publisher
    if _publisher is None:
        _publisher = GamePublisher()
    return _publisher

def get_publisher() -> GamePublisher:
    if _publisher is None:
        raise RuntimeError("Publisher not initialized.")
    return _publisher

async def stop_publisher():
    if _publisher:
        await _publisher.stop()