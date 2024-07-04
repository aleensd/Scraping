class ServiceException(Exception):
    def __init__(self, message: str) -> None:
        self.message: str = message

    def __str__(self) -> str:
        return f'[{self.__class__.__name__}] {self.message}'


class EnvVariableMissingError(ServiceException):
    def __init__(self, env_var_name: str) -> None:
        message: str = (
            'Service misconfiguration.'
            f' Environment variable {env_var_name} is missing.'
        )

        super().__init__(message=message)