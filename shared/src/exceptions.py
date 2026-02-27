class AppException(Exception):
    error_code: str = "AppException"

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if "error_code" not in cls.__dict__:
            cls.error_code = cls.__name__

class EntityNotFound(AppException):
    pass

class UnexpectedException(AppException):
    pass

class EntityAlreadyExists(AppException):
    pass

class InvalidOperation(AppException):
    pass

class GameAlreadyStarted(EntityAlreadyExists):
    pass

class AttributeAlreadyRevealed(EntityAlreadyExists):
    pass

class NoRevealRequired(InvalidOperation):
    pass

class VotingAlreadyStarted(EntityAlreadyExists):
    pass

class UserAlreadyVoted(EntityAlreadyExists):
    pass

class VotingTargetNotFound(EntityNotFound):
    pass

class UserAlreadyKicked(InvalidOperation):
    pass

class UserIsNotPlayer(InvalidOperation):
    pass

class InvalidVotingStateError(AppException):
    pass

def build_error_code_map():
    result = {}
    queue = [AppException]
    while queue:
        cls = queue.pop()
        result[cls.error_code] = cls
        queue.extend(cls.__subclasses__())
    return result