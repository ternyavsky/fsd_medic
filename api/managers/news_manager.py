from django.db.models import Count, Subquery

from api.managers.base_manager import BaseQuerySet, BaseManager


class NewsQuerySet(BaseQuerySet):



    def filter_by_user(self, user=None):
        if user:
            clinic_news = self.filter(clinic=user.clinic)
            disease_news = self.filter(disease__in=user.disease.all())
            disease_news = disease_news.annotate(
                quant_likes=Count("like", distinct=True),
                images=Subquery()
            ).order_by("-quant_likes")
            clinic_news = clinic_news.annotate(
                quant_likes=Count("like", distinct=True)
            ).order_by("-quant_likes")
            news = disease_news.union(clinic_news).order_by("-created_at")
            return news
        else:
            return self.annotate(quant_likes=Count("like", distinct=True)).order_by("-quant_likes")


class NewsManager(BaseManager):
    def get_queryset(self):
        return NewsQuerySet(self.model)

    def filter_by_user(self, user=None):
        return self.get_queryset().filter_by_user(user)
