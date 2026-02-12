from apscheduler.schedulers.background import BackgroundScheduler
from gmail_service import fetch_unread_emails, mark_as_read
from mainAgent import mainAgent
import logging

logger = logging.getLogger("cron_job")
logging.basicConfig(level=logging.INFO)

scheduler = BackgroundScheduler()


def process_unread_emails():
    """Fetch unread emails from Gmail and process each through the agent."""
    logger.info("Cron job: Checking for unread emails...")

    try:
        emails = fetch_unread_emails(max_results=1)
    except FileNotFoundError:
        logger.warning("Gmail not authenticated. Skipping. Visit /auth/google to authenticate.")
        return
    except Exception as e:
        logger.error(f"Failed to fetch emails: {e}")
        return

    if not emails:
        logger.info("No new unread emails found.")
        return

    logger.info(f"Found {len(emails)} unread email(s). Processing...")

    for email in emails:
        try:
            formatted_query = (
                f"From: {email['from_email']}\n"
                f"Subject: {email['subject']}\n\n"
                f"{email['body']}"
            )

            logger.info(f"Processing email from {email['from_email']}: {email['subject']}")

            result = mainAgent(query=formatted_query, history=None)
            # result = {"response": "Agent response placeholder "} # Replace with actual agent call if needed

            logger.info(f"Agent response: {result.get('response', 'No response')[:200]}")

            mark_as_read(email["id"])
            logger.info(f"Marked email {email['id']} as read.")

        except Exception as e:
            logger.error(f"Error processing email {email.get('id', 'unknown')}: {e}")


def start_scheduler():
    """Start the background scheduler (runs every 5 minutes)."""
    scheduler.add_job(
        process_unread_emails,
        trigger="interval",
        minutes=2,
        id="email_processor",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("Email processing scheduler started (runs every 5 minutes).")


def stop_scheduler():
    """Gracefully shut down the scheduler."""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Email processing scheduler stopped.")
