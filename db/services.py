def generate_cache_key(prefix, **kwargs):
    # Пример: "chat_messages_1_2" для чата с ID 1 и пользователем с ID 2
    key_parts = [str(value) for value in kwargs.values()]
    return f"{prefix}_{'_'.join(key_parts)}"