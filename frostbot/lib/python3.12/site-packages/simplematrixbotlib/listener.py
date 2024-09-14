from typing import TYPE_CHECKING, Callable

from nio import Event, MatrixRoom, RoomMessage, RoomMessageText, ReactionEvent

if TYPE_CHECKING:
    from simplematrixbotlib.bot import Bot


class Listener:

    def __init__(self, bot: "Bot"):
        self._bot = bot
        self._registry = []
        self._startup_registry = []

    def on_custom_event(self, event: Event) -> Callable[[Callable[..., None]], None]:

        def wrapper(func):
            if [func, event] in self._registry:
                func()
            else:
                self._registry.append([func, event])

        return wrapper

    def on_message_event(self, func: Callable[[MatrixRoom, RoomMessageText], None]) -> None:
        if [func, RoomMessageText] in self._registry:
            func()
        else:
            self._registry.append([func, RoomMessageText])

    def on_reaction_event(self, func: Callable[[MatrixRoom, ReactionEvent, str], None]) -> None:

        async def wrapper(room, event):
            await func(room, event, event.key)

        self._registry.append([wrapper, ReactionEvent])

    def on_startup(self, func: Callable[[str], None]) -> None:
        if func in self._startup_registry:
            func()
        else:
            self._startup_registry.append(func)