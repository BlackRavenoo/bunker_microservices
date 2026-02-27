from services.game_service.app.domain.dto import CharacterDTO
from services.game_service.app.domain.dto.update import CharacterBatchUpdateDTO, CharacterUpdateDTO, GameUpdateDTO, NullableFieldUpdate, NumericFieldUpdate, NumericOperation
from services.game_service.app.domain.services.voting import calculate_voting_result
from services.game_service.app.domain.uow import UnitOfWork
from services.game_service.app.infrastructure.messaging.rabbitmq import GamePublisher
from shared.src.enums import CharacterStatus, GameStatus, VotingResult
from shared.src.events import GameEnded, NewRoundStarted, PlayerVoted, VotingEnded, VotingStarted
from shared.src.exceptions import InvalidVotingStateError, UserAlreadyKicked, UserAlreadyVoted, UserIsNotPlayer, VotingTargetNotFound

class VotingService:
    def __init__(self, uow: UnitOfWork, publisher: GamePublisher):
        self.uow = uow
        self.publisher = publisher

    async def _start_new_round(self, game_id: str, count_to_kick: NumericFieldUpdate):
        await self.uow.games.update_game(
            game_id=game_id,
            update_data=GameUpdateDTO(
                status=GameStatus.Discussion,
                count_to_kick=count_to_kick
            )
        )

        await self.uow.characters.update_active_characters_by_game_id(
            game_id=game_id,
            updates=CharacterUpdateDTO(
                status=CharacterStatus.Alive,
                needs_to_reveal=True,
                voted_for=NullableFieldUpdate(
                    value=None
                )
            )
        )

    async def _revote(self, game_id: str, member_ids: list[int]):
        updates = [
            CharacterBatchUpdateDTO(
                id=id,
                status=CharacterStatus.Protected
            )
            for id in member_ids
        ]

        await self.uow.characters.update_characters(
            updates=updates
        )

        await self.uow.characters.update_active_characters_by_game_id(
            game_id=game_id,
            updates=CharacterUpdateDTO(
                voted_for=NullableFieldUpdate(
                    value=None
                )
            )
        )

    async def start_voting(self, game_id: str):
        async with self.uow as uow:
            await uow.games.start_voting(game_id=game_id)

            characters: list[CharacterDTO] = await uow.characters.get_active_characters(game_id)

            await uow.commit()

        await self.publisher.publish(VotingStarted(
            game_id=game_id,
            characters=[char.into_shared() for char in characters]
        ))

    async def vote(self, game_id: str, user_id: str, target_user_id: str):
        async with self.uow as uow:
            res = await uow.characters.get_characters_without_attrs(
                game_id=game_id,
                user_ids=[user_id, target_user_id]
            )

            user = next((c for c in res if c.user_id == user_id), None)
            target = next((c for c in res if c.user_id == target_user_id), None)

            if not target or target.is_kicked:
                raise VotingTargetNotFound()

            if not user:
                raise UserIsNotPlayer()

            if user.is_kicked:
                raise UserAlreadyKicked()
            
            if user.voted_for is not None:
                raise UserAlreadyVoted()

            await uow.characters.vote(
                game_id=game_id,
                user_id=user_id,
                target_id=target.id
            )

            voting_participants = await uow.games.get_voting_participants(
                game_id=game_id,
            )

            is_all_voted = all([det.is_voted for det in voting_participants])

            if is_all_voted:
                metadata = await uow.games.get_voting_metadata(game_id=game_id)

                calc_res = calculate_voting_result(
                    details=voting_participants,
                    metadata=metadata
                )

                if calc_res.result in [
                    VotingResult.KICK,
                    VotingResult.KICK_AND_REVOTE
                ]:
                    updates = [
                        CharacterBatchUpdateDTO(
                            id=candidate.id,
                            status=CharacterStatus.Kicked
                        )
                        for candidate in calc_res.candidates_to_kick
                    ]

                    await uow.characters.update_characters(
                        updates=updates
                    )
                
                    if calc_res.result == VotingResult.KICK:
                        await self._start_new_round(
                            game_id=game_id,
                            count_to_kick=NumericFieldUpdate(
                                value=1
                            )
                        )
                    else:
                        await self.uow.games.update_game(
                            game_id=game_id,
                            update_data=GameUpdateDTO(
                                count_to_kick=NumericFieldUpdate(
                                    value=len(calc_res.candidates_to_kick),
                                    operation=NumericOperation.DECREMENT
                                )
                            )
                        )

                        await self.uow.characters.update_active_characters_by_game_id(
                            game_id=game_id,
                            updates=CharacterUpdateDTO(
                                voted_for=NullableFieldUpdate(
                                    value=None
                                )
                            )
                        )

                if calc_res.result in [
                    VotingResult.REVOTE_DECISION,
                    VotingResult.TIE_DECISION
                ]:
                    await uow.games.update_game(
                        game_id=game_id,
                        update_data=GameUpdateDTO(
                            status=GameStatus.Discussion
                        )
                    )

                if calc_res.result == VotingResult.REVOTE:
                    await self._revote(
                        game_id=game_id,
                        member_ids=[member.id for member in calc_res.remaining_members]
                    )

            await uow.commit()

        await self.publisher.publish(PlayerVoted(
            game_id=game_id,
            user_id=user_id,
            user_name=user.username,
            target_id=target_user_id,
            target_name=target.username,
            vote_details=[p.into_shared() for p in voting_participants]
        ))

        if is_all_voted:
            await self.publisher.publish(VotingEnded(
                game_id=game_id,
                candidates_for_kick=[c.into_shared() for c in calc_res.candidates_to_kick],
                remaining_members=[c.into_shared() for c in calc_res.remaining_members],
                voting_result=calc_res.result
            ))

            if calc_res.result == VotingResult.KICK:
                if len(calc_res.remaining_members) <= metadata.places_count:
                    await self.publisher.publish(GameEnded(
                        game_id=game_id,
                    ))
                else:
                    await self.publisher.publish(NewRoundStarted(
                        game_id=game_id,
                        count_to_kick=1
                    ))

    async def skip_voting(self, game_id: str):
        async with self.uow as uow:
            details = await uow.games.get_voting_participants(
                game_id=game_id
            )

            metadata = await uow.games.get_voting_metadata(
                game_id=game_id
            )

            calc_res = calculate_voting_result(
                details=details,
                metadata=metadata
            )

            if calc_res.result not in [
                VotingResult.REVOTE_DECISION,
                VotingResult.TIE_DECISION
            ]:
                raise InvalidVotingStateError()
            
            await self._start_new_round(
                game_id=game_id,
                count_to_kick=NumericFieldUpdate(
                    value=1,
                    operation=NumericOperation.INCREMENT
                )
            )

            await self.publisher.publish(NewRoundStarted(
                game_id=game_id,
                count_to_kick=metadata.count_to_kick + 1
            ))
    
    async def revote(self, game_id: int):
        async with self.uow as uow:
            details = await uow.games.get_voting_participants(
                game_id=game_id
            )

            metadata = await uow.games.get_voting_metadata(
                game_id=game_id
            )

            calc_res = calculate_voting_result(
                details=details,
                metadata=metadata
            )

            if calc_res.result not in [
                VotingResult.REVOTE_DECISION,
                VotingResult.TIE_DECISION
            ]:
                raise InvalidVotingStateError()
            
            await self._revote(
                game_id=game_id,
                member_ids=[member.id for member in calc_res.remaining_members]
            )

    async def kick_all_candidates(self, game_id: int):
        async with self.uow as uow:
            details = await uow.games.get_voting_participants(
                game_id=game_id
            )

            metadata = await uow.games.get_voting_metadata(
                game_id=game_id
            )

            calc_res = calculate_voting_result(
                details=details,
                metadata=metadata
            )

            if calc_res.result != VotingResult.TIE_DECISION:
                raise InvalidVotingStateError()
            
            updates = {
                CharacterBatchUpdateDTO(
                    id=candidate.id,
                    status=CharacterStatus.Kicked
                )
                for candidate in calc_res.candidates_to_kick
            }

            await uow.characters.update_characters(
                updates=updates
            )