import re

class Match:
    """
    Class with methods to filter events

    ...

    """

    def __init__(self, room, event, bot) -> None:
        """
        Initializes the simplematrixbotlib.Match class.

        ...

        Parameters
        ----------
        room : nio.rooms.MatrixRoom
            The bot developer will use the room parameter of the handler function for this.
    
        event : nio.events.room_events.Event
            The bot developer will use the event parameter of the handler function for this.
        
        bot : simplematrixbotlib.Bot
            The bot developer will use the bot's instance of the simplematrixbotlib.Bot class for this.

        """
        self.room = room
        self.event = event
        self._bot = bot

    def is_from_userid(self, userid):
        """
        Parameters
        ----------
        userid : str
            The userid of a user.

        Returns
        -------
        boolean
            Returns True if the event was sent from the specified userid
        """
        return self.event.sender == userid

    def is_from_allowed_user(self):
        """
        Returns
        -------
        boolean
            Returns True if the event was sent from an allowed userid
        """
        allowlist = self._bot.config.allowlist
        blocklist = self._bot.config.blocklist
        sender = self.event.sender
        # if there is no explicit allowlist, default to allow
        is_allowed = False if len(allowlist) > 0 else True

        for regex in allowlist:
            if regex.fullmatch(sender):
                is_allowed = True
                break

        for regex in blocklist:
            if regex.fullmatch(sender):
                is_allowed = False
                break

        return is_allowed

    def is_not_from_this_bot(self):
        """
        
        Returns
        -------
        boolean
            Returns True if the event is from a user that is not this bot.
        """
        return not self.is_from_userid(self._bot.async_client.user_id)


class MessageMatch(Match):
    """
    Class with methods to filter message events

    ...

    """

    def __init__(self, room, event, bot, prefix="") -> None:
        """
        Initializes the simplematrixbotlib.MessageMatch class.

        ...

        Parameters
        ----------
        room : nio.rooms.MatrixRoom
            The bot developer will use the room parameter of the handler function for this.
    
        event : nio.events.room_events.Event
            The bot developer will use the event parameter of the handler function for this.
        
        bot : simplematrixbotlib.Bot
            The bot developer will use the bot's instance of the simplematrixbotlib.Bot class for this.

        prefix : str, Optional
            The bot developer will specify a prefix, the prefix is the beginning of messages that are intended to be commands, usually "!", "/" or similar.

        """
        super().__init__(room, event, bot)
        self._prefix = prefix

    def formatted_body(self):
        """

        Returns
        -------
        Optional[str]
            Returns the string after removing html balise used for a reply.
        """
                
        if self.event.formatted_body:
            if "<mx-reply>" in self.event.formatted_body:
                return re.sub(r'<mx-reply>.*?</mx-reply>', '', self.event.formatted_body)
            else:
                return self.event.formatted_body
        return None

    def command(self, command=None, case_sensitive=True):
        """
        Parameters
        ----------
        command : str, Optional
            Beginning of messages that are intended to be commands, but after the prefix; e.g. "help".

        case_sensitive : bool, Optional
            Whether the string should be matched case sensitive.

        Returns
        -------
        boolean
            Returns True if the string after the prefix and before the first space is the same as the given arg.
        
        str
            Returns the string after the prefix and before the first space if no arg is passed to this method.
        """

        if self._prefix == self.event.body[0:len(self._prefix)]:
            body_without_prefix = self.event.body[len(self._prefix):]
        else:
            body_without_prefix = self.event.body

        if not body_without_prefix:
            return []
        
        loc = self.formatted_body()
        if loc:
            body_without_prefix = loc[1:]

        if command:
            return (body_without_prefix.split()[0] == command
                    if case_sensitive else
                    body_without_prefix.split()[0].lower() == command.lower())
        else:
            return body_without_prefix.split()[0]

    def prefix(self):
        """

        Returns
        -------
        boolean
            Returns True if the message begins with the prefix, and False otherwise. If there is no prefix specified during the creation of this MessageMatch object, then return True.
        """

        loc = self.formatted_body()
        if loc:
            return loc.startswith(self._prefix)

        return self.event.body.startswith(self._prefix)

    def args(self):
        """
        
        Returns
        -------
        list
            Returns a list of strings that are the "words" of the message, except for the first "word", which would be the command.
        """
            
        loc = self.formatted_body()
        if loc:
            return loc[1:].split()[1:]

        return self.event.body.split()[1:]

    def contains(self, string):
        """
        
        Returns
        -------
        boolean
            Returns True if the string argument is found within the body of the message.
        """

        loc = self.formatted_body()
        if loc:
            return string in loc[1:]

        return string in self.event.body
