from db.queries import *
from datetime import date, datetime
from django.core.cache import cache
from django.db.models import Count, Q, Subquery, F
def user_profile_data(pk):
    users = cache.get_or_set("users", get_users())
    users = users.filter(pk=pk) if pk else users
    access = cache.get_or_set("access", get_access())
    access = access.filter(user_id=pk) if pk else access   
    notes = cache.get_or_set("notes", get_notes())  
    curr_notes = notes.filter(user_id__in=Subquery(users.values("id")), status="Passed")
    process_notes = notes.filter(user_id__in=Subquery(users.values("id")), status="In processing")
    miss_notes = notes.filter(user_id__in=Subquery(users.values("id")), time_start__gt=datetime.now())
    result = {  
        "user": users,  
        "curr_notes": curr_notes, #Текущие записи
        "process_notes": process_notes, # Неустановленные записи
        "miss_notes": miss_notes, # Пропущенные записи
        "access": access
    }
    return result


def country_profile_data(name):
    cities = cache.get_or_set("cities", get_cities())
    cities = cities.filter(country__name=name) if name else cities
    cities = cities.annotate(
        quant_centers=Count("center", distinct=True),
        quant_centers_today=Count("center", distinct=True, filter=Q(center__created_at__date=date.today())),
        quant_clinics=Count("clinic", distinct=True),
        quant_clinics_today=Count("clinic", distinct=True, filter=Q(clinic__created_at__date=date.today())),
        quant_users=Count("user", distinct=True),
        quant_users_today=Count("user", distinct=True, filter=Q(user__created_at__date=date.today())),
    )
    cities = cities.order_by(-(F("quant_centers") + F("quant_clinics") + F("quant_users")))
    countries = cache.get_or_set("countries", get_countries())
    countries = countries.filter(name=name) if name else countries
    countries = countries.annotate(
        quant_clinics=Count("clinic", distinct=True),
        quant_clinics_today=Count("clinic", distinct=True, filter=Q(clinic__created_at__date=date.today())),
        quant_users=Count("user", distinct=True),
        quant_users_today=Count("user", distinct=True, filter=Q(user__created_at__date=date.today())),
        quant_doctors=Count("doctor", distinct=True),
        quant_doctors_today=Count("doctor", distinct=True),
    )
    result = {
        "cities": cities,
        "country": countries
    }
    return result

def city_profile_data():
    cities = cache.get_or_set("cities", get_cities())
    cities = cities.annotate(
        quant_centers=Count("center", distinct=True),
        quant_centers_today=Count("center", distinct=True, filter=Q(center__created_at__date=date.today())),
        quant_clinics=Count("clinic", distinct=True),
        quant_clinics_today=Count("clinic", distinct=True, filter=Q(clinic__created_at__date=date.today())),
        quant_users=Count("user", distinct=True),
        quant_users_today=Count("user", distinct=True, filter=Q(user__created_at__date=date.today())),
    )
    return cities


def center_profile_data(pk):
    centers = cache.get_or_set("centers", get_centers())
    centers = centers.filter(pk=pk) if pk else centers
    centers = centers.annotate(
        online_notes=Count("note", filter=Q(note__online=True)),
        offline_notes=Count("note", filter=Q(note__online=False)),
        visit_online=Count("note", distinct=True,
                            filter=Q(note__online=True, note__time_start__day=date.today().day)),
        visit_offline=Count("note", distinct=True,
                            filter=Q(note__online=False, note__time_start__day=date.today().day)),
    )
    users = cache.get_or_set("users", get_users())
    users_centers = users.filter(centers__id__in=centers.values("id"))
    result = users_centers 
    obj = {
        "center": centers,
        "pacients": result
    }
    return obj


def clinic_profile_data(pk):
    clinics = cache.get_or_set("clinics", get_clinics())
    clinics = clinics.filter(pk=pk) if pk else clinics
    clinics = clinics.annotate(
        online_notes=Count("note", filter=Q(note__online=True)),
        offline_notes=Count("note", filter=Q(note__online=False)),
        visit_online=Count("note", filter=Q(note__online=True, note__time_start__day=date.today().day)),
        visit_offline=Count("note", filter=Q(note__online=False, note__time_start__day=date.today().day))
    )
    users = cache.get_or_set("users", get_users())
    users = users.filter(clinic__id__in=clinics.values("id"))
    return {
        "clinic": clinics,
        "pacients": users
    }


def main_page_data():
    users = get_users()
    created_today = users.filter(created_at__date=date.today()).count()
    group_1 = users.filter(birthday__year__lte=date.today().year - 10, birthday__year__gte=date.today().year - 20)
    group1_mans = group_1.filter(sex="Мужчина").count()
    group1_womans = group_1.filter(sex="Женщина").count()

    group_2 = users.filter(birthday__year__lte=date.today().year - 20, birthday__year__gte=date.today().year - 30)
    group2_mans = group_2.filter(sex="Мужчина").count()
    group2_womans = group_2.filter(sex="Женщина").count()


    group_3 = users.filter(birthday__year__lte=date.today().year - 30 , birthday__year__gte=date.today().year - 40)
    group3_mans = group_3.filter(sex="Мужчина").count()
    group3_womans = group_3.filter(sex="Женщина").count()

    group_4 = users.filter(birthday__year__lte=date.today().year - 40, birthday__year__gte=date.today().year - 50)
    group4_mans = group_4.filter(sex="Мужчина").count()
    group4_womans = group_4.filter(sex="Женщина").count()

    group_5 = users.filter(birthday__year__lte=date.today().year - 50, birthday__year__gte=date.today().year - 60)
    group5_mans = group_5.filter(sex="Мужчина").count()
    group5_womans = group_5.filter(sex="Женщина").count()

    group_6 = users.filter(birthday__year__lte=date.today().year - 60, birthday__year__gte=date.today().year - 70)
    group6_mans = group_6.filter(sex="Мужчина").count()
    group6_womans = group_6.filter(sex="Женщина").count()

    # print(group_1.first().woman)
    diseases = cache.get_or_set("disease", get_disease())
    diseases = diseases.annotate(
        most_count=Count("user")
    )
    diseases = diseases.order_by("-most_count")

    data = {
        "diseases": diseases,
        "_10_20": [{"man" : group1_mans, "woman": group1_womans}],
        "_20_30": [{"man": group2_mans, "woman": group2_womans}],
        "_30_40": [{"man": group3_mans, "woman": group3_womans}],
        "_40_50": [{"man": group4_mans, "woman": group4_womans}],
        "_50_60": [{"man": group5_mans, "woman": group5_womans}],
        "_60_70": [{"man": group6_mans, "woman": group6_womans}],
        "created_today": created_today
    }
    print(group_1)
    return data