from services.game_service.app.domain.dto import VotingParticipant, VotingDistribution, VotingMetadata
from shared.src.enums import VotingResult

def calculate_voting_result(details: list[VotingParticipant], metadata: VotingMetadata) -> VotingDistribution:
    max_votes = max(detail.votes_count for detail in details)

    candidates = []
    remaining = []

    for detail in details:
        if detail.votes_count == max_votes:
            candidates.append(detail)
        else:
            remaining.append(detail)

    if len(candidates) < metadata.count_to_kick:
        res = VotingResult.KICK_AND_REVOTE
    elif len(candidates) == metadata.count_to_kick:
        res = VotingResult.KICK
    elif len(candidates) == 2 \
        and metadata.count_to_kick == 1 \
        and len(details) - metadata.places_count >= 2:
            res = VotingResult.TIE_DECISION
    elif len(details) - metadata.places_count >= 2:
        res = VotingResult.REVOTE_DECISION
    else:
        res = VotingResult.REVOTE

    return VotingDistribution(
        result=res,
        candidates_to_kick=candidates,
        remaining_members=remaining
    )