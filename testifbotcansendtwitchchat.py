from twitchAPI.chat import Chat, ChatEvent, EventData
import asyncio

TARGET_CHANNEL = 'Queensell'  # replace with your target channel

async def on_ready(event: EventData):
    await event.chat.join_room(TARGET_CHANNEL)
    print("Bot is ready!!")

    # Test sending a chat message
    await event.chat.send_message(TARGET_CHANNEL, "Hello! This is a test message from the bot.")
    print("Test message sent to chat!")

async def on_message(msg):
    print(f"{msg.user.display_name} - {msg.text}")

async def run_bot():
    from twitchAPI.twitch import Twitch
    from twitchAPI.oauth import UserAuthenticator
    from twitchAPI.type import AuthScope

    import dontLeak  # your client_id and client_secret

    USER_SCOPE = [AuthScope.CHAT_READ, AuthScope.CHAT_EDIT, AuthScope.CHANNEL_MANAGE_BROADCAST]

    bot = await Twitch(dontLeak.client_id, dontLeak.client_secret)
    auth = UserAuthenticator(bot, USER_SCOPE)
    token, refresh_token = await auth.authenticate()
    await bot.set_user_authentication(token, USER_SCOPE, refresh_token)

    chat = await Chat(bot)
    chat.register_event(ChatEvent.READY, on_ready)
    chat.register_event(ChatEvent.MESSAGE, on_message)
    chat.start()

    try:
        input("Press Enter to stop the bot...\n")
    finally:
        chat.stop()
        await bot.close()
        print("Bot stopped.")

if __name__ == "__main__":
    asyncio.run(run_bot())
