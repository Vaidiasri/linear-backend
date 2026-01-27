"""
Email template builder - Separation of concerns
Complexity: 1 per function
"""


class EmailTemplate:
    """Email template builder with static methods"""

    @staticmethod
    def welcome(username: str) -> tuple[str, str]:
        """Generate welcome email subject and body"""
        subject = f"Welcome to Linear Backend, {username}! 🎉"
        body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f5f5f5;">
                <div style="max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                    <h1 style="color: #333;">Welcome {username}! 👋</h1>
                    <p style="color: #666; font-size: 16px; line-height: 1.6;">
                        Thanks for joining our platform. We're excited to have you on board!
                    </p>
                    <p style="color: #666; font-size: 16px; line-height: 1.6;">
                        Get started by exploring our features and creating your first project.
                    </p>
                    <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee;">
                        <p style="color: #999; font-size: 14px;">
                            Best regards,<br>
                            <strong>The Linear Backend Team</strong>
                        </p>
                    </div>
                </div>
            </body>
        </html>
        """
        return subject, body

    @staticmethod
    def password_reset(reset_token: str) -> tuple[str, str]:
        """Generate password reset email"""
        reset_link = f"https://yourapp.com/reset-password?token={reset_token}"
        subject = "Password Reset Request 🔐"
        body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f5f5f5;">
                <div style="max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                    <h2 style="color: #333;">Password Reset Request</h2>
                    <p style="color: #666; font-size: 16px; line-height: 1.6;">
                        We received a request to reset your password. Click the button below to proceed:
                    </p>
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{reset_link}" style="background: #007bff; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">
                            Reset Password
                        </a>
                    </div>
                    <p style="color: #999; font-size: 14px;">
                        This link will expire in 1 hour.
                    </p>
                    <p style="color: #999; font-size: 14px;">
                        If you didn't request this, please ignore this email.
                    </p>
                </div>
            </body>
        </html>
        """
        return subject, body

    @staticmethod
    def issue_notification(
        issue_title: str, action: str, actor: str
    ) -> tuple[str, str]:
        """Generate issue notification email"""
        subject = f"Issue {action}: {issue_title}"
        body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f5f5f5;">
                <div style="max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                    <h2 style="color: #333;">Issue {action}</h2>
                    <p style="color: #666; font-size: 16px; line-height: 1.6;">
                        <strong>{actor}</strong> {action.lower()} an issue:
                    </p>
                    <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <h3 style="color: #333; margin: 0;">{issue_title}</h3>
                    </div>
                    <p style="color: #666; font-size: 14px;">
                        Click here to view the issue and take action.
                    </p>
                </div>
            </body>
        </html>
        """
        return subject, body

    @staticmethod
    def daily_report(report_date: str) -> tuple[str, str]:
        """Generate daily report email"""
        subject = f"Daily Report - {report_date}"
        body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; padding: 20px;">
                <h1>Daily Report</h1>
                <p>Report generated at: {report_date}</p>
                <h2>Summary</h2>
                <ul>
                    <li>Total Issues: TBD</li>
                    <li>Resolved Today: TBD</li>
                    <li>Pending: TBD</li>
                </ul>
            </body>
        </html>
        """
        return subject, body
