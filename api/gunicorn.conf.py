"""Gunicorn settings for the Render web service."""

workers = 1


def post_worker_init(worker):
    """Start the existing email scheduler once in the single web worker."""
    import app as api

    if api.SCHEDULER_AVAILABLE and api.config.SMTP_ENABLED and not api.scheduler.running:
        api.scheduler.start()
        worker.log.info("Expiration email scheduler started")
