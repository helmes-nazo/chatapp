import os
import random

import django
from dateutil import tz
from faker import Faker

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "intern.settings")
django.setup()

from myapp.models import Talk, CustomUser

fakegen = Faker(["ja_JP"])

def create_users(n):

    users = [
        CustomUser(username=fakegen.user_name(), email=fakegen.ascii_safe_email())
        for _ in range(n)
    ]

    CustomUser.objects.bulk_create(users, ignore_conflicts=True)

    my_id = CustomUser.objects.get(username="admin").id

    user_ids = CustomUser.objects.exclude(id=my_id).values_list("id", flat=True)

    talks = []
    for _ in range(len(user_ids)):
        sent_talk = Talk(
            talk_from_id=my_id,
            talk_to_id=random.choice(user_ids),
            talk=fakegen.text(),
        )
        received_talk = Talk(
            talk_from_id=random.choice(user_ids),
            talk_to_id=my_id,
            talk=fakegen.text(),
        )
        talks.extend([sent_talk, received_talk])
    Talk.objects.bulk_create(talks, ignore_conflicts=True)

    talks = Talk.objects.order_by("-time")[: 2 * len(user_ids)]
    for talk in talks:
        talk.time = fakegen.date_time_this_year(tzinfo=tz.gettz("Asia/Tokyo"))
    Talk.objects.bulk_update(talks, fields=["time"])


if __name__ == "__main__":
    print("creating users ...", end="")
    create_users(1000)
    print("done")