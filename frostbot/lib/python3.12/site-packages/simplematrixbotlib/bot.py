import asyncio
import sys
from typing import Optional
import simplematrixbotlib as botlib
from nio import SyncResponse, AsyncClient
import cryptography
import os

from simplematrixbotlib.auth import Creds
from simplematrixbotlib.config import Config


class Bot:
    """
    A class for the bot library user to interact with.
    
    ...

    Attributes
    ----------
    api : simplematrixbotlib.Api
        An instance of the simplematrixbotlib.Api class.
    
    """

    def __init__(self, creds: Creds, config: Optional[Config] = None):
        """
        Initializes the simplematrixbotlib.Bot class.

        Parameters
        ----------
        creds : simplematrixbotlib.Creds
        config : simplematrixbotlib.Config

        """

        self.creds = creds
        if config:
            self.config = config
            self._need_allow_homeserver_users = False
        else:
            self._need_allow_homeserver_users = True
            self.config = botlib.Config()
        self.api = botlib.Api(self.creds, self.config)
        self.listener = botlib.Listener(self)
        self.async_client: AsyncClient = None
        self.callbacks: botlib.Callbacks = None

    async def main(self) -> None:
        try:
            self.creds.session_read_file()
        except cryptography.fernet.InvalidToken:
            print("Invalid Stored Token")
            print("Regenerating token from provided credentials")
            os.remove(self.creds._session_stored_file)
            self.creds.session_read_file()

        if not (await botlib.api.check_valid_homeserver(self.creds.homeserver
                                                        )):
            raise ValueError("Invalid Homeserver")

        await self.api.login()

        self.async_client = self.api.async_client

        resp = await self.async_client.sync(timeout=self.config.timeout, full_state=self.config.first_sync_full
                                            )  #Ignore prior messages if full_state=False (default)

        if isinstance(resp, SyncResponse):
            print(
                f"Connected to {self.async_client.homeserver} as {self.async_client.user_id} ({self.async_client.device_id})"
            )
            if self.config.encryption_enabled:
                key = self.async_client.olm.account.identity_keys['ed25519']
                print(
                    f"This bot's public fingerprint (\"Session key\") for one-sided verification is: "
                    f"{' '.join([key[i:i+4] for i in range(0, len(key), 4)])}")

        self.creds.session_write_file()

        if self._need_allow_homeserver_users:
            # allow (only) users from our own homeserver by default
            _, hs = botlib.api.split_mxid(self.api.async_client.user_id)
            self.config.allowlist = set([f"(.+):{hs}"])

        self.callbacks = botlib.Callbacks(self.async_client, self)
        await self.callbacks.setup_callbacks()

        for action in self.listener._startup_registry:
            for room_id in self.async_client.rooms:
                await action(room_id)

        await self.async_client.sync_forever(timeout=3000, full_state=True, set_presence=self.config._set_presence)

    def run(self) -> None:
        """
        Runs the bot.

        """
        asyncio.run(self.main())
