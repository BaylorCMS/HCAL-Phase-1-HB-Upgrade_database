import sys
import django

sys.path.insert(0, '/home/django/testing_database_hb/card_db')
django.setup()

from qie_cards.models import QieCard, Attempt, Test
from django.db import transaction

@transaction.atomic
def set_card_status(qiecard):
    tests = Test.objects.all()
    status = {}
    status["total"] = len(tests.filter(required=True))
    status["passed"] = 0
    failedAny = False
    no_result = False

    for test in tests:
        attemptList = Attempt.objects.filter(card=qiecard.pk, test_type = test.pk).order_by("attempt_number")
        if attemptList:
            last = attemptList[len(attemptList) - 1]
            if not last.revoked and test.required:
                if last.overwrite_pass:
                    status["passed"] += 1
                elif last.passed():
                    status["passed"] += 1
                elif last.empty_test():
                    no_result = True
                else:
                    failedAny = True

    if status["total"] == status["passed"]:
        qiecard.status = True
    elif failedAny:
        qiecard.status = False
    elif no_result:
        qiecard.status = None
    else:
        qiecard.status = None

    qiecard.save()

