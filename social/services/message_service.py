from api.models import News


def get_message_data(chat_id, validates_data):
    message_data = validates_data.copy()
    del message_data["user_ids"]
    del message_data["center_ids"]
    message_data["chat_id"] = chat_id
    return message_data
    


def first_message_validate(data):
    news_id = data.get("news_id")
    text = data.get("text")
    if news_id is None and text is None:
        return False, "news, text", "В сообении должна быть либо новость, либо текст"
    
    if news_id is not None and not News.objects.filter(id=news_id).exists():
        return False, "news_id", "Не существует такой новости"
    return True, "", ""

def first_message_create(chat_id, validated_data):
    validated_data[""]
    MessageGetSerializer