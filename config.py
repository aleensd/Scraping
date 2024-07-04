from __future__ import annotations

import os

from exceptions import ServiceException, EnvVariableMissingError


class Config:
    _instance: Config | None = None

    def __new__(cls) -> Config:
        try:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
            cls._driver_path = cls.get_required_env('DRIVER_PATH')
            cls._url = cls.get_required_env('URL')
            cls._pdf_base_url = cls.get_required_env('PDF_BASE_URL')
            cls._download_default_directory=cls.get_required_env('DOWNLOAD_DEFAULT_DIRECTORY')
            return cls._instance
        except ServiceException as e:
            raise e

    @classmethod
    def get_required_env(cls, env: str) -> str:
        value: str | None = os.getenv(env)
        if value is None:
            # fail early if environment does not have the required env variable.
            raise EnvVariableMissingError(env_var_name=env)

        return value

    @property
    def driver_path(self) -> str:
        return self._driver_path

    @property
    def url(self) -> str:
        return self._url

    @property
    def pdf_base_url(self) -> str:
        return self._pdf_base_url

    @property
    def download_default_directory(self) -> str:
        return self._download_default_directory

