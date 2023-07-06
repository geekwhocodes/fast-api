import abc


class SingletonMeta(type):
    """
    The Singleton class can be implemented in different ways in Python. Some
    possible methods include: base class, decorator, metaclass. We will use the
    metaclass because it is best suited for this purpose.
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        """
        Possible changes to the value of the `__init__` argument do not affect
        the returned instance.
        """
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class GeoLocator(metaclass=SingletonMeta):
    """ """

    @classmethod
    def __subclasshook__(cls, subclass):
        return (
            hasattr(subclass, "get_address")
            and callable(subclass.get_address)
            and hasattr(subclass, "get_geocode")
            and callable(subclass.get_geocode)
            or NotImplemented
        )

    @abc.abstractmethod
    async def get_address(self, lat: float, long: float):
        """Get address using geocode apis"""
        raise NotImplementedError

    @abc.abstractmethod
    async def get_geocode(self, adsress: str):
        """Extract text from the data set"""
        raise NotImplementedError
