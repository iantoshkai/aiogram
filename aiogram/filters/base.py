from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Awaitable, Callable, Dict, Union

if TYPE_CHECKING:
    from aiogram.dispatcher.event.handler import CallbackType, FilterObject


class Filter(ABC):
    """
    If you want to register own filters like builtin filters you will need to write subclass
    of this class with overriding the :code:`__call__`
    method and adding filter attributes.
    """

    if TYPE_CHECKING:
        # This checking type-hint is needed because mypy checks validity of overrides and raises:
        # error: Signature of "__call__" incompatible with supertype "BaseFilter"  [override]
        # https://mypy.readthedocs.io/en/latest/error_code_list.html#check-validity-of-overrides-override
        __call__: Callable[..., Awaitable[Union[bool, Dict[str, Any]]]]
    else:  # pragma: no cover

        @abstractmethod
        async def __call__(self, *args: Any, **kwargs: Any) -> Union[bool, Dict[str, Any]]:
            """
            This method should be overridden.

            Accepts incoming event and should return boolean or dict.

            :return: :class:`bool` or :class:`Dict[str, Any]`
            """
            pass

    def __invert__(self) -> "_InvertFilter":
        return invert_f(self)

    def update_handler_flags(self, flags: Dict[str, Any]) -> None:
        pass

    def _signature_to_string(self, *args: Any, **kwargs: Any) -> str:
        items = [repr(arg) for arg in args]
        items.extend([f"{k}={v!r}" for k, v in kwargs.items()])

        return f"{type(self).__name__}({', '.join(items)})"

    def __str__(self) -> str:
        return self._signature_to_string()

    def __await__(self):  # type: ignore # pragma: no cover
        # Is needed only for inspection and this method is never be called
        return self.__call__


class _InvertFilter(Filter):
    __slots__ = ("target",)

    def __init__(self, target: "FilterObject") -> None:
        self.target = target

    async def __call__(self, *args: Any, **kwargs: Any) -> Union[bool, Dict[str, Any]]:
        return not bool(await self.target.call(*args, **kwargs))

    def __str__(self) -> str:
        return f"~{self.target.callback}"


def invert_f(target: "CallbackType") -> _InvertFilter:
    from aiogram.dispatcher.event.handler import FilterObject

    return _InvertFilter(target=FilterObject(target))
