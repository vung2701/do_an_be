from django_cron import CronJobBase, Schedule
from .models import ReadingList
import pytz
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
class UpdateRemainJob(CronJobBase):
    RUN_AT_TIMES = ['00:00']
    TIMEZONE = None

    schedule = Schedule(run_at_times=RUN_AT_TIMES)
    code = 'unreg_user.job.UpdateRemainJob'

    def do(self):
        current_time = datetime.now()
        logger.info(f"Current time in system timezone: {current_time}")
        if current_time.day == 1 and current_time.hour == 0 and current_time.minute == 0:
            ReadingList.objects.all().update(remain=2)
            logger.info("Cron job UpdateRemainJob ran successfully and set remain to 2.")
