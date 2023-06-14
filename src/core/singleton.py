from typing import Any, Optional


class Singleton(type):
    def __init__(self, *args, **kwargs):
        self.__instance__ = None
        super().__init__(*args, **kwargs)
        pass

    def __call__(self, *args, **kwargs) -> Optional[Any]:
        if self.__instance__ is None:
            self.__instance__ = super().__call__(*args, **kwargs)
        return self.__instance__
        pass
