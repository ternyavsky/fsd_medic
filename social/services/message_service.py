from api.models import News, Note


def get_message_data(chat_id, validates_data):
    message_data = validates_data.copy()
    del message_data["user_ids"]
    del message_data["center_ids"]
    message_data["chat"] = chat_id
    return message_data
    


def first_message_validate(data):
    news_id = data.get("news")
    text = data.get("text")
    note = data.get("note")
    if news_id is None and text is None and note is not None:
        return False, "news, text, note", "В сообении должна быть либо новость, либо текст, либо заметка"
    
    if news_id is not None and not News.objects.filter(id=news_id).exists():
        return False, "news", "Не существует такой новости"
    
    if note is not None and not Note.objects.filter(id=note).exists():
        return False, "note", "Не существует такой заметки"
    return True, "", ""

