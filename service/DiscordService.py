import datetime

async def fetch_messages(client, channel_id, days=1):
    channel = client.get_channel(channel_id)

    if not channel:
        print(f"Channel with id {channel_id} not found.")
        return
    
    now = datetime.datetime.now(datetime.timezone.utc)
    time_threshold = now - datetime.timedelta(days=days)

    messages = []

    async for msg in channel.history(limit=None):
        if msg.created_at.replace(tzinfo=datetime.timezone.utc) > time_threshold:
            messages.append(msg)
        else:
            break
    
    return messages