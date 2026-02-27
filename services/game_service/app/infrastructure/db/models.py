import nanoid
from sqlalchemy import BigInteger, Boolean, Column, Enum, ForeignKey, Index, Integer, SmallInteger, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from services.game_service.app.infrastructure.db.session import Base
from shared.src.enums import ActionTarget, ActionType, ActionValue, AttributeCategory, BunkerElementType, CharacterStatus, GameStatus

class Game(Base):
    __tablename__ = "games"

    id = Column(String(16), primary_key=True, nullable=False, unique=True, default=lambda: nanoid.generate(size=16))
    host_id = Column(String(128), nullable=False)
    status = Column(Enum(GameStatus), nullable=False, default=GameStatus.BeforeStart)

    count_to_kick = Column(SmallInteger, nullable=False, default=1)
    places_count = Column(SmallInteger)
    force_voting = Column(Boolean, nullable=False, default=False)

    catastrophe_id = Column(SmallInteger, ForeignKey("catastrophes.id", ondelete="RESTRICT"))

    catastrophe = relationship("Catastrophe", uselist=False)
    characters = relationship("Character", backref="game", cascade="all, delete-orphan")
    bunker_elements = relationship(
        "BunkerElement",
        secondary="game_bunker_elements",
        cascade="all, delete"
    )

class Catastrophe(Base):
    __tablename__ = "catastrophes"

    id = Column(SmallInteger, primary_key=True, autoincrement=True)
    name = Column(String(128), nullable=False, unique=True)
    description = Column(String(512), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)

class BunkerElement(Base):
    __tablename__ = "bunker_elements"

    id = Column(Integer, primary_key=True, autoincrement=True)
    category = Column(Enum(BunkerElementType), nullable=False)
    value = Column(String, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)

    __table_args__ = (UniqueConstraint("category", "value", name="_be_category_value_uc"),)

class GameBunkerElement(Base):
    __tablename__ = "game_bunker_elements"

    game_id = Column(String(16), ForeignKey("games.id", ondelete="CASCADE"), primary_key=True)
    bunker_element_id = Column(Integer, ForeignKey("bunker_elements.id", ondelete="RESTRICT"), primary_key=True)

class Attribute(Base):
    __tablename__ = "attributes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    category = Column(Enum(AttributeCategory), nullable=False)
    value = Column(String, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)

    __table_args__ = (UniqueConstraint("category", "value", name="_at_category_value_uc"),)

class ActionCard(Base):
    __tablename__ = "action_cards"

    id = Column(Integer, primary_key=True, autoincrement=True)
    action = Column(Enum(ActionType), nullable=False)
    value = Column(Enum(ActionValue), nullable=False)
    target = Column(Enum(ActionTarget), nullable=False)
    info = Column(String, nullable=True)

    __table_args__ = (UniqueConstraint("action", "value", "info", "target", name="_action_value_info_target_uc"),)

class CharacterActionCard(Base):
    __tablename__ = "character_action_cards"

    character_id = Column(BigInteger, ForeignKey("characters.id", ondelete="CASCADE"), primary_key=True)
    action_card_id = Column(Integer, ForeignKey("action_cards.id", ondelete="CASCADE"), primary_key=True)
    is_used = Column(Boolean, nullable=False, default=False)

class Character(Base):
    __tablename__ = "characters"
    __table_args__ = (
        UniqueConstraint("user_id", "game_id", name="_user_game_uc"),
        Index("idx_characters_attributes_gin", "attributes", postgresql_using="gin")
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(128), nullable=False)
    game_id = Column(String(16), ForeignKey("games.id", ondelete="CASCADE"), index=True)
    user_id = Column(String(128), nullable=False, index=True)
    status = Column(Enum(CharacterStatus), nullable=False, default=CharacterStatus.Alive)
    voted_for = Column(BigInteger, ForeignKey("characters.id", ondelete="SET NULL"), default=None)
    needs_to_reveal = Column(Boolean, nullable=False, default=True)

    attributes = Column(JSONB)

    action_cards = relationship(
        ActionCard,
        secondary="character_action_cards",
        cascade="all, delete"
    )