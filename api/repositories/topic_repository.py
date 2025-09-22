from api.models import Topic

class TopicRepository:
    def __init__(self):
        pass

    def get(self, topic_id: str):
        return Topic.objects.get(topic_id=topic_id)