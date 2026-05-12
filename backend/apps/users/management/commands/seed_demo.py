from django.core.management.base import BaseCommand

from apps.articles.models import Article
from apps.notes.models import Highlight
from apps.users.models import User


class Command(BaseCommand):
    help = "Seed the database with demo data"

    def handle(self, *args, **options):
        # Create demo user
        user, created = User.objects.get_or_create(
            email="demo@example.com",
            defaults={"name": "Demo User"},
        )
        if created:
            user.set_password("demo1234")
            user.save()
            self.stdout.write(self.style.SUCCESS("Created demo user: demo@example.com / demo1234"))
        else:
            self.stdout.write("Demo user already exists.")

        # Create sample articles
        articles_data = [
            {
                "title": "The Rise of Large Language Models",
                "source_url": "https://example.com/llm-rise",
                "raw_text": (
                    "Large language models have transformed the field of artificial intelligence. "
                    "Starting with GPT-2 in 2019, these models have grown exponentially in size and "
                    "capability. They can now generate human-quality text, translate languages, write "
                    "code, and answer questions across virtually any domain. The implications for "
                    "industries ranging from healthcare to education are profound."
                ),
                "summary": (
                    "Large language models have revolutionized AI since GPT-2's release in 2019. "
                    "These models have grown dramatically in scale and abilities, now capable of "
                    "text generation, translation, coding, and question answering. Their impact "
                    "spans healthcare, education, and many other industries."
                ),
                "key_points": [
                    "LLMs began gaining prominence with GPT-2 in 2019",
                    "Model sizes have grown exponentially over the past few years",
                    "Capabilities include text generation, translation, and code writing",
                    "Applications span healthcare, education, and other industries",
                    "The technology continues to evolve rapidly",
                ],
                "tags": ["ai", "machine-learning", "nlp", "technology"],
            },
            {
                "title": "Understanding Climate Change Policies",
                "source_url": "https://example.com/climate-policy",
                "raw_text": (
                    "Climate change policies are evolving rapidly as governments worldwide respond "
                    "to the growing urgency of environmental degradation. The Paris Agreement set "
                    "ambitious targets for reducing greenhouse gas emissions. Carbon pricing "
                    "mechanisms, renewable energy subsidies, and green infrastructure investments "
                    "are among the key policy tools being deployed. However, implementation varies "
                    "significantly between developed and developing nations."
                ),
                "summary": (
                    "Global climate change policies are rapidly evolving in response to environmental "
                    "urgency. The Paris Agreement established emission reduction targets, while "
                    "governments deploy tools like carbon pricing and renewable energy subsidies. "
                    "Implementation remains uneven between developed and developing nations."
                ),
                "key_points": [
                    "The Paris Agreement set global emission reduction targets",
                    "Carbon pricing is a key policy mechanism",
                    "Renewable energy subsidies drive clean energy adoption",
                    "Green infrastructure investments are increasing",
                    "Developed and developing nations face different challenges",
                    "Policy implementation varies significantly worldwide",
                ],
                "tags": ["climate", "policy", "environment", "energy"],
            },
            {
                "title": "The Future of Remote Work",
                "source_url": "https://example.com/remote-work",
                "raw_text": (
                    "Remote work has become a permanent fixture of the modern workplace. What began "
                    "as a pandemic necessity has evolved into a preferred work arrangement for "
                    "millions. Companies are adopting hybrid models that balance in-office "
                    "collaboration with remote flexibility. Tools for virtual collaboration continue "
                    "to improve, and studies show that productivity often increases with remote work."
                ),
                "summary": (
                    "Remote work has transitioned from pandemic necessity to permanent workplace "
                    "fixture. Hybrid models are becoming the norm, combining in-office collaboration "
                    "with remote flexibility. Collaboration tools continue to mature, and research "
                    "suggests productivity benefits from remote arrangements."
                ),
                "key_points": [
                    "Remote work is now a permanent feature of the modern workplace",
                    "Hybrid models balance office and remote work",
                    "Virtual collaboration tools continue to improve",
                    "Studies show productivity often increases with remote work",
                    "Companies are redesigning office spaces for collaboration",
                ],
                "tags": ["remote-work", "productivity", "workplace", "technology"],
            },
        ]

        for article_data in articles_data:
            article, created = Article.objects.get_or_create(
                user=user,
                title=article_data["title"],
                defaults=article_data,
            )
            if created:
                Highlight.objects.create(
                    article=article,
                    text=article.key_points[0] if article.key_points else article.summary[:80],
                    color="yellow",
                    source="summary",
                )
                self.stdout.write(self.style.SUCCESS(f"Created article: {article.title}"))
            else:
                self.stdout.write(f"Article already exists: {article.title}")

        self.stdout.write(self.style.SUCCESS("\nSeed complete!"))
