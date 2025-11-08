"""
Email service for notifications (v0.5.0)
"""
import logging
import html
from typing import Optional
from consultantos.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Email service for sending notifications"""
    
    def __init__(self):
        # In production, integrate with SendGrid, AWS SES, or similar
        self.enabled = settings.environment == "production"
    
    def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None
    ) -> bool:
        """
        Send an email
        
        Args:
            to: Recipient email address
            subject: Email subject
            body: Plain text body
            html_body: Optional HTML body
        
        Returns:
            True if sent successfully, False otherwise
        """
        if not self.enabled:
            logger.info(f"[EMAIL SERVICE] Would send email to {to}: {subject}")
            logger.debug(f"Body: {body}")
            return True
        
        # In production, implement actual email sending
        # Example with SendGrid:
        # import sendgrid
        # sg = sendgrid.SendGridAPIClient(api_key=settings.sendgrid_api_key)
        # message = sendgrid.Mail(
        #     from_email=settings.from_email,
        #     to_emails=to,
        #     subject=subject,
        #     plain_text_content=body,
        #     html_content=html_body
        # )
        # response = sg.send(message)
        # return response.status_code == 202
        
        logger.warning("Email service not configured for production")
        return False
    
    def send_share_notification(
        self,
        to: str,
        report_id: str,
        shared_by: str,
        share_url: str,
        message: Optional[str] = None
    ) -> bool:
        """Send notification when a report is shared"""
        subject = f"Report Shared with You - ConsultantOS"
        body = f"""
A report has been shared with you by {shared_by}.

Report ID: {report_id}
Access URL: {share_url}

{f"Message: {message}" if message else ""}

You can view the report by clicking the link above.
        """
        
        # Escape user-provided content to prevent XSS
        escaped_shared_by = html.escape(shared_by, quote=True)
        escaped_report_id = html.escape(report_id, quote=True)
        escaped_share_url = html.escape(share_url, quote=True)
        escaped_message = html.escape(message, quote=True) if message else None
        
        html_body = f"""
        <html>
        <body>
            <h2>Report Shared with You</h2>
            <p>A report has been shared with you by <strong>{escaped_shared_by}</strong>.</p>
            <p><strong>Report ID:</strong> {escaped_report_id}</p>
            <p><a href="{escaped_share_url}">View Report</a></p>
            {f"<p><strong>Message:</strong> {escaped_message}</p>" if escaped_message else ""}
        </body>
        </html>
        """
        
        return self.send_email(to, subject, body, html_body)
    
    def send_comment_notification(
        self,
        to: str,
        report_id: str,
        commenter: str,
        comment: str,
        comment_url: str
    ) -> bool:
        """Send notification when a comment is added"""
        subject = f"New Comment on Report - ConsultantOS"
        body = f"""
{commenter} commented on report {report_id}:

"{comment}"

View the comment: {comment_url}
        """
        
        # Escape user-provided content to prevent XSS
        escaped_commenter = html.escape(commenter, quote=True)
        escaped_report_id = html.escape(report_id, quote=True)
        escaped_comment = html.escape(comment, quote=True)
        escaped_comment_url = html.escape(comment_url, quote=True)
        
        html_body = f"""
        <html>
        <body>
            <h2>New Comment</h2>
            <p><strong>{escaped_commenter}</strong> commented on report <strong>{escaped_report_id}</strong>:</p>
            <blockquote>{escaped_comment}</blockquote>
            <p><a href="{escaped_comment_url}">View Comment</a></p>
        </body>
        </html>
        """
        
        return self.send_email(to, subject, body, html_body)


# Global email service instance
_email_service: Optional[EmailService] = None


def get_email_service() -> EmailService:
    """Get or create email service instance"""
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service

