from fast_depends.msgspec import MsgSpecSerializer
from faststream.rabbit import RabbitBroker, RabbitExchange, ExchangeType
from services.tg_bot.app.core.config import settings
from shared.src.consts import GAME_EXCHANGE_NAME

_broker: RabbitBroker | None = None

exchange = RabbitExchange(
    name=GAME_EXCHANGE_NAME,
    type=ExchangeType.TOPIC,
    durable=True,
)

async def init_broker() -> RabbitBroker:
    global _broker
    _broker = RabbitBroker(
        settings.rabbitmq_url,
        app_id="tg_bot",
        serializer=MsgSpecSerializer()
    )
    return _broker

async def shutdown_broker():
    if _broker:
        await _broker.stop()

def get_broker() -> RabbitBroker:
    if _broker is None:
        raise RuntimeError("Broker not initialized")
    return _broker