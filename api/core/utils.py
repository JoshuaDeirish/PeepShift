from datetime import timedelta
from zoneinfo import Zoneinfo
from django.utils import timezone

def business_date_for(location, moment=None):
      if moment is None:
            moment = timezone.now()

      local = moment.astimezone(Zoneinfo(location.timezone))

      if local.hour < location.business_day_cutoff_hour:
            local = local - timedelta(days=1)

      return local.date()
     