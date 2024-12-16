from sqlalchemy.ext.declarative import DeclarativeMeta
from abc import ABCMeta


class ModelABCMeta(DeclarativeMeta, ABCMeta):
    """
    This metaclass is used as a base metaclass for defining abstract models in the ORM.
    It combines the functionality of the `DeclarativeMeta` metaclass and the `ABCMeta` metaclass.
    """
    pass
