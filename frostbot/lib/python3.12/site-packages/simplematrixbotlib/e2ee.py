from nio import KeyVerificationEvent, MatrixRoom, RoomMessageUnknown, ToDeviceEvent


async def key_verification_to_device_callback(event: KeyVerificationEvent):
    print("key verification to device")
    print(event)


async def key_verification_event_callback(room: MatrixRoom, event: RoomMessageUnknown):
    print("key verification to room")
    print(event)
