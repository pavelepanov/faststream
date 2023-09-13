from abc import abstractproperty
from typing import Dict

from faststream.asyncapi.schema.channels import Channel


class AsyncAPIOperation:
    """A class representing an asynchronous API operation.

    Attributes:
        name : name of the API operation

    Methods:
        schema() : returns the schema of the API operation as a dictionary of channel names and channel objects
    !!! note

        The above docstring is autogenerated by docstring-gen library (https://docstring-gen.airt.ai)
    """

    @abstractproperty
    def name(self) -> str:
        raise NotImplementedError()

    def schema(self) -> Dict[str, Channel]:  # pragma: no cover
        return {}
