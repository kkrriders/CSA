"""
Email service for sending notifications.
"""
from typing import List, Dict
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from jinja2 import Environment, FileSystemLoader
from pathlib import Path

from app.core.config import get_settings
from app.models.notification import EmailTemplate

settings = get_settings()

# Email configuration
conf = ConnectionConfig(
    MAIL_USERNAME=settings.get("MAIL_USERNAME", ""),
    MAIL_PASSWORD=settings.get("MAIL_PASSWORD", ""),
    MAIL_FROM=settings.get("MAIL_FROM", "noreply@adaptivelearning.com"),
    MAIL_PORT=settings.get("MAIL_PORT", 587),
    MAIL_SERVER=settings.get("MAIL_SERVER", "smtp.gmail.com"),
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

# Jinja2 environment for templates
templates_dir = Path(__file__).parent.parent / "templates" / "emails"
templates_dir.mkdir(parents=True, exist_ok=True)
jinja_env = Environment(loader=FileSystemLoader(str(templates_dir)))


class EmailService:
    """Service for sending emails."""

    def __init__(self):
        self.mail = FastMail(conf)
        self.jinja_env = jinja_env

    async def send_email(
        self,
        recipients: List[str],
        subject: str,
        body: str,
        html: bool = True
    ) -> bool:
        """Send an email."""
        try:
            message = MessageSchema(
                subject=subject,
                recipients=recipients,
                body=body,
                subtype=MessageType.html if html else MessageType.plain
            )

            await self.mail.send_message(message)
            return True
        except Exception as e:
            print(f"Error sending email: {e}")
            return False

    async def send_template_email(
        self,
        recipients: List[str],
        template: EmailTemplate
    ) -> bool:
        """Send an email using a template."""
        try:
            # Load and render template
            jinja_template = self.jinja_env.get_template(f"{template.template_name}.html")
            html_body = jinja_template.render(**template.data)

            return await self.send_email(
                recipients=recipients,
                subject=template.subject,
                body=html_body,
                html=True
            )
        except Exception as e:
            print(f"Error sending template email: {e}")
            return False

    async def send_review_reminder(
        self,
        recipient: str,
        user_name: str,
        due_reviews: int,
        topics: List[str]
    ) -> bool:
        """Send a review reminder email."""
        template = EmailTemplate(
            template_name="review_reminder",
            subject=f"You have {due_reviews} reviews due today!",
            data={
                "user_name": user_name,
                "due_reviews": due_reviews,
                "topics": topics
            }
        )

        return await self.send_template_email([recipient], template)

    async def send_weekly_report(
        self,
        recipient: str,
        user_name: str,
        report_data: Dict
    ) -> bool:
        """Send a weekly progress report."""
        template = EmailTemplate(
            template_name="weekly_report",
            subject="Your Weekly Learning Progress Report",
            data={
                "user_name": user_name,
                **report_data
            }
        )

        return await self.send_template_email([recipient], template)

    async def send_milestone_email(
        self,
        recipient: str,
        user_name: str,
        milestone: str,
        achievement: str
    ) -> bool:
        """Send a milestone celebration email."""
        template = EmailTemplate(
            template_name="milestone",
            subject=f"Congratulations! {milestone}",
            data={
                "user_name": user_name,
                "milestone": milestone,
                "achievement": achievement
            }
        )

        return await self.send_template_email([recipient], template)

    async def send_streak_reminder(
        self,
        recipient: str,
        user_name: str,
        streak_days: int
    ) -> bool:
        """Send a streak reminder email."""
        template = EmailTemplate(
            template_name="streak_reminder",
            subject=f"Keep your {streak_days}-day streak alive!",
            data={
                "user_name": user_name,
                "streak_days": streak_days
            }
        )

        return await self.send_template_email([recipient], template)

    async def send_exam_ready_email(
        self,
        recipient: str,
        user_name: str,
        document_title: str,
        readiness_score: float
    ) -> bool:
        """Send exam readiness notification."""
        template = EmailTemplate(
            template_name="exam_ready",
            subject=f"You're ready for {document_title}!",
            data={
                "user_name": user_name,
                "document_title": document_title,
                "readiness_score": readiness_score
            }
        )

        return await self.send_template_email([recipient], template)
