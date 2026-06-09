from django.db import models


class Tool(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    function_path = models.CharField(max_length=200)
    parameters_schema = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Tool"
        verbose_name_plural = "Tools"


class Agent(models.Model):
    MODEL_CHOICES = [
        ("claude-sonnet-4-5", "Claude Sonnet 4.5"),
        ("claude-haiku-4-5", "Claude Haiku 4.5"),
    ]

    slug = models.SlugField(unique=True)
    display_name = models.CharField(max_length=100)
    model = models.CharField(
        max_length=50,
        choices=MODEL_CHOICES,
        default="claude-sonnet-4-5",
    )
    system_prompt = models.TextField()
    description = models.TextField(blank=True)

    tools = models.ManyToManyField(
        "Tool",
        through="AgentTool",
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.display_name

    class Meta:
        verbose_name = "Agent"
        verbose_name_plural = "Agents"
        ordering = ["-created_at"]


class AgentTool(models.Model):
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE)
    tool = models.ForeignKey(Tool, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("agent", "tool")
        verbose_name = "Agent Tool"
        verbose_name_plural = "Agent Tools"


class Conversation(models.Model):
    agent = models.ForeignKey(
        Agent,
        on_delete=models.CASCADE,
        related_name="conversations",
    )
    title = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title or f"Conversation #{self.id}"

    class Meta:
        verbose_name = "Conversation"
        verbose_name_plural = "Conversations"
        ordering = ["-created_at"]


