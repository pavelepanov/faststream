from typing import Any, Awaitable, Callable, Generic, List, Optional, Union
from unittest.mock import MagicMock

import anyio

from faststream._compat import Self
from faststream.broker.message import StreamMessage
from faststream.broker.types import (
    AsyncPublisherProtocol,
    MsgType,
    P_HandlerParams,
    T_HandlerReturn,
    WrappedHandlerCall,
    WrappedReturn,
)
from faststream.types import SendableMessage


class FakePublisher:
    """A class to represent a fake publisher.

    Attributes:
        method : a callable method that takes arguments and returns an awaitable sendable message

    Methods:
        publish : asynchronously publishes a message with optional correlation ID and additional keyword arguments
    !!! note

        The above docstring is autogenerated by docstring-gen library (https://docstring-gen.airt.ai)
    """

    def __init__(self, method: Callable[..., Awaitable[SendableMessage]]) -> None:
        """Initialize an object.

        Args:
            method: A callable that takes any number of arguments and returns an awaitable sendable message.
        !!! note

            The above docstring is autogenerated by docstring-gen library (https://docstring-gen.airt.ai)
        """
        self.method = method

    async def publish(
        self,
        message: SendableMessage,
        correlation_id: Optional[str] = None,
        **kwargs: Any,
    ) -> Optional[SendableMessage]:
        """Publish a message.

        Args:
            message: The message to be published.
            correlation_id: Optional correlation ID for the message.
            **kwargs: Additional keyword arguments.

        Returns:
            The published message.
        !!! note

            The above docstring is autogenerated by docstring-gen library (https://docstring-gen.airt.ai)
        """
        return await self.method(message, correlation_id=correlation_id, **kwargs)


class HandlerCallWrapper(Generic[MsgType, P_HandlerParams, T_HandlerReturn]):
    """A generic class to wrap handler calls.

    Attributes:
        mock : MagicMock object used for mocking
        event : an anyio.Event object used for synchronization

        _wrapped_call : WrappedHandlerCall object representing the wrapped handler call
        _original_call : original handler call
        _publishers : list of AsyncPublisherProtocol objects

    Methods:
        __new__ : Create a new instance of the class
        __init__ : Initialize the instance
        __call__ : Call the wrapped handler
        set_wrapped : Set the wrapped handler call
        call_wrapped : Call the wrapped handler
        wait_call : Wait for the handler call to complete
    !!! note

        The above docstring is autogenerated by docstring-gen library (https://docstring-gen.airt.ai)
    """

    mock: MagicMock
    event: Optional[anyio.Event]

    _wrapped_call: Optional[WrappedHandlerCall[MsgType, T_HandlerReturn]]
    _original_call: Callable[P_HandlerParams, T_HandlerReturn]
    _publishers: List[AsyncPublisherProtocol]

    def __new__(
        cls,
        call: Union[
            "HandlerCallWrapper[MsgType, P_HandlerParams, T_HandlerReturn]",
            Callable[P_HandlerParams, T_HandlerReturn],
        ],
    ) -> Self:
        """Create a new instance of the class.

        Args:
            call: An instance of "HandlerCallWrapper" or a callable object

        Returns:
            An instance of the class

        Note:
            If the "call" argument is already an instance of the class, it is returned as is. Otherwise, a new instance of the class is created using the superclass's __new__ method.
        !!! note

            The above docstring is autogenerated by docstring-gen library (https://docstring-gen.airt.ai)
        """
        if isinstance(call, cls):
            return call
        else:
            return super().__new__(cls)

    def __init__(
        self,
        call: Callable[P_HandlerParams, T_HandlerReturn],
    ):
        """Initialize a handler.

        Args:
            call: A callable object that represents the handler function.

        Attributes:
            _original_call: The original handler function.
            _wrapped_call: The wrapped handler function.
            _publishers: A list of publishers.
            mock: A MagicMock object.
            event: The event associated with the handler.
            __name__: The name of the handler function.
        !!! note

            The above docstring is autogenerated by docstring-gen library (https://docstring-gen.airt.ai)
        """
        if not isinstance(call, HandlerCallWrapper):
            self._original_call = call
            self._wrapped_call = None
            self._publishers = []
            self.mock = MagicMock()
            self.event = None
            self.__name__ = getattr(self._original_call, "__name__", "undefined")

    def __call__(
        self,
        *args: P_HandlerParams.args,
        **kwargs: P_HandlerParams.kwargs,
    ) -> T_HandlerReturn:
        """Calls the object as a function.

        Args:
            *args: Positional arguments to be passed to the function.
            **kwargs: Keyword arguments to be passed to the function.

        Returns:
            The return value of the function.
        !!! note

            The above docstring is autogenerated by docstring-gen library (https://docstring-gen.airt.ai)
        """
        self.mock(*args, **kwargs)
        if self.event is not None:
            self.event.set()
        return self._original_call(*args, **kwargs)

    def set_wrapped(
        self, wrapped: WrappedHandlerCall[MsgType, T_HandlerReturn]
    ) -> None:
        """Set the wrapped handler call.

        Args:
            wrapped: The wrapped handler call to set
        !!! note

            The above docstring is autogenerated by docstring-gen library (https://docstring-gen.airt.ai)
        """
        self._wrapped_call = wrapped

    def call_wrapped(
        self,
        message: StreamMessage[MsgType],
    ) -> Union[
        Optional[WrappedReturn[T_HandlerReturn]],
        Awaitable[Optional[WrappedReturn[T_HandlerReturn]]],
    ]:
        """Calls the wrapped function with the given message.

        Args:
            message: The message to be passed to the wrapped function.

        Returns:
            The result of the wrapped function call.

        Raises:
            AssertionError: If `set_wrapped` has not been called before calling this function.
            AssertionError: If the broker has not been started before calling this function.
        !!! note

            The above docstring is autogenerated by docstring-gen library (https://docstring-gen.airt.ai)
        """
        assert self._wrapped_call, "You should use `set_wrapped` first"  # nosec B101
        assert self.event, "You should start the broker first"  # nosec B101
        self.mock(message.decoded_body)
        self.event.set()
        return self._wrapped_call(message)

    async def wait_call(self, timeout: Optional[float] = None) -> None:
        """Waits for a call with an optional timeout.

        Args:
            timeout: Optional timeout in seconds

        Raises:
            AssertionError: If the broker is not started

        Returns:
            None
        !!! note

            The above docstring is autogenerated by docstring-gen library (https://docstring-gen.airt.ai)
        """
        assert self.event, "You should start the broker first"  # nosec B101
        with anyio.fail_after(timeout):
            await self.event.wait()
