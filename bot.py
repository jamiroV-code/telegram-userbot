import asyncio
import json
from telethon import TelegramClient, events

# 🔑 Your Telegram API credentials
api_id = 35416739
api_hash = "8885b9631465ca06edc06952188f2b91"

# 🟢 Channels to forward from
source_channels = [
    "cryptonarratives1",
    "asymmetric_thinker",
    "modocapital",
    "AnteaterAmazon",
    "infinityhedge",
    "marketsAlpha",
    "blockchainwhispersbaby",
    "moonbagsnotes",
    "bitcoin4wealth"
]

# 🟡 Channel to forward to
target_channel = "dataflow123"

# 💾 File to store last message IDs
STATE_FILE = "state.json"


# 📦 Load saved state
def load_state():
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    except:
        return {}


# 💾 Save state
def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)


async def main():
    client = TelegramClient("userbot", api_id, api_hash)
    await client.start()
    print("Userbot running with memory...")

    state = load_state()

    # 🔁 STEP 1: Catch up missed messages (smarter first run)
    for channel in source_channels:
        entity = await client.get_entity(channel)

        # SMARTER FIRST RUN: Only grab the last message if first time
        if channel not in state:
            last_msg = await client.get_messages(entity, limit=1)
            if last_msg:
                state[channel] = last_msg[0].id
                save_state(state)
            continue

        last_id = state.get(channel, 0)

        print(f"Checking missed messages for {channel}...")

        async for msg in client.iter_messages(entity, min_id=last_id, reverse=True):
            text = msg.text or ""
            formatted = f"[SOURCE: {entity.title}]\n\n{text}"

            await client.send_message(target_channel, formatted)

            # update state
            state[channel] = msg.id
            save_state(state)

    # ⚡ STEP 2: Live messages
    @client.on(events.NewMessage)
    async def handler(event):
        chat = await event.get_chat()
        username = getattr(chat, "username", None)

        if username not in source_channels:
            return

        last_id = state.get(username, 0)

        if event.message.id <= last_id:
            return

        text = event.message.text or ""
        formatted = f"[SOURCE: {chat.title}]\n\n{text}"

        await client.send_message(target_channel, formatted)

        # update state
        state[username] = event.message.id
        save_state(state)

    await client.run_until_disconnected()


asyncio.run(main())