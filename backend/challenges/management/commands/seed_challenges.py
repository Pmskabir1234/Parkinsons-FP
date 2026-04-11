from django.core.management.base import BaseCommand

from challenges.models import Challenge


class Command(BaseCommand):
    help = "Create MVP challenges (one per category) if missing."

    def handle(self, *args, **options):
        specs = [
            {
                "slug": "bug-sum-positive-off-by-one",
                "category": Challenge.Category.BUG_FIX,
                "title": "Fix the off-by-one in sum_positive",
                "description": (
                    "The function should sum all strictly positive numbers in the list. "
                    "A classic indexing bug slipped in — find it before the release build."
                ),
                "starter_code": '''def sum_positive(nums):
    s = 0
    for i in range(len(nums) - 1):
        if nums[i] > 0:
            s += nums[i]
    return s

if __name__ == "__main__":
    print(sum_positive([1, -2, 3, 4]))
''',
                "time_limit_seconds": 120,
                "points": 15,
                "validator": {
                    "kind": "python_io",
                    "language": "python",
                    "tests": [
                        {"stdin": "", "expected_stdout": "8\n"},
                    ],
                },
            },
            {
                "slug": "code-factorial",
                "category": Challenge.Category.CODE_CHALLENGE,
                "title": "Implement factorial",
                "description": (
                    "Implement factorial(n) for n >= 0. "
                    "This is validated against hidden I/O tests; keep the entrypoint block as-is."
                ),
                "starter_code": '''def factorial(n):
    # Return n! for integers n >= 0
    pass

if __name__ == "__main__":
    print(factorial(5))
    print(factorial(0))
''',
                "time_limit_seconds": 180,
                "points": 20,
                "validator": {
                    "kind": "python_io",
                    "language": "python",
                    "tests": [
                        {"stdin": "", "expected_stdout": "120\n1\n"},
                    ],
                },
            },
            {
                "slug": "scenario-http-success",
                "category": Challenge.Category.DEV_SCENARIO,
                "title": "REST API basics",
                "description": (
                    "You are reviewing an incident report. "
                    "Pick the HTTP status that most clearly indicates a successful response to a typical GET request."
                ),
                "starter_code": "",
                "time_limit_seconds": 60,
                "points": 10,
                "validator": {
                    "kind": "mcq",
                    "prompt": "Which status code represents a successful GET?",
                    "options": [
                        "500 Internal Server Error",
                        "404 Not Found",
                        "200 OK",
                        "301 Moved Permanently",
                    ],
                    "correct_index": 2,
                },
            },
        ]

        created = 0
        for row in specs:
            obj, was_created = Challenge.objects.update_or_create(
                slug=row["slug"],
                defaults={
                    "category": row["category"],
                    "title": row["title"],
                    "description": row["description"],
                    "starter_code": row["starter_code"],
                    "time_limit_seconds": row["time_limit_seconds"],
                    "points": row["points"],
                    "validator": row["validator"],
                },
            )
            if was_created:
                created += 1
                self.stdout.write(self.style.SUCCESS(f"Created {obj.slug}"))
            else:
                self.stdout.write(f"Updated {obj.slug}")

        self.stdout.write(self.style.SUCCESS(f"Done. New: {created}"))
