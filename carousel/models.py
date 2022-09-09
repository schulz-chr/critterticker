from django.db import models
from datetime import datetime, time, date, timedelta
from critterticker.settings import BASE_DIR


# Create your models here.


class Month(models.Model):
    # <object.month> returns integer
    MONTH_CHOICES = [
        (1, "January"),
        (2, "February"),
        (3, "March"),
        (4, "April"),
        (5, "May"),
        (6, "June"),
        (7, "July"),
        (8, "August"),
        (9, "September"),
        (10, "October"),
        (11, "November"),
        (12, "December")
    ]
    month_num = models.IntegerField(choices=MONTH_CHOICES)

    def get_abb(self):
        return str(self)[0]

    def __str__(self):
        return self.get_month_num_display()

    def get_int(self):
        return self.month_num


class DiveFish(models.Model):
    SHADOW_MOVEMENT_CHOICES = [
        ('ST', 'stationary'),
        ('SL-', 'very slow'),
        ('SL', 'slow'),
        ('M', 'medium'),
        ('F', 'fast'),
        ('F+', 'very fast')
    ]

    SIZE_CHOICES = [
        ('XS', 'tiny'),
        ('S', 'small'),
        ('M', 'medium'),
        ('L', 'large'),
        ('LT', 'long & thin'),
        ('XL', 'very large'),
        ('XLF', 'very large with fin'),
        ('XXL', 'huge')
    ]

    # id always like "df1", "df20", "df31"...
    id = models.CharField(primary_key=True, max_length=5, default='')
    name = models.CharField(max_length=50, unique=True)
    price = models.IntegerField(default=0)
    movement = models.CharField(max_length=15, choices=SHADOW_MOVEMENT_CHOICES)
    catches_req = models.IntegerField('df catches required', default=0)
    month = models.ManyToManyField(Month, blank=True)
    size = models.CharField(max_length=20, default='XS', choices=SIZE_CHOICES)

    # time interval for daily availability
    interval_start = models.TimeField(default=time.min)
    interval_end = models.TimeField(default=time.max)

    # time interval for df with two available time spans
    interval2_start = models.TimeField(default=time.min)
    interval2_end = models.TimeField(default=time.min)

    def get_hours_display(self):
        start = self.interval_start
        end = self.interval_end
        start2 = self.interval2_start
        end2 = self.interval2_end
        # check if first interval includes whole day (time(0)>time(23,59,59))
        if start == time(0) and end == time(23, 59, 59):
            return "All day"
        # check if no second interval has been provided
        elif start2 == time(0) and end2 == time(0):
            start_formatted = start.strftime('%I').strip('0') + ' ' + start.strftime('%p')
            end_formatted = end.strftime('%I').strip('0') + ' ' + end.strftime('%p')
            return f"{start_formatted} to {end_formatted}"
        else:  # means: there is a second time interval for availability
            display_string = ''
            start_formatted = start.strftime('%I').strip('0') + ' ' + start.strftime('%p')
            end_formatted = end.strftime('%I').strip('0') + ' ' + end.strftime('%p')
            start2_formatted = start2.strftime('%I').strip('0') + ' ' + start2.strftime('%p')
            end2_formatted = end2.strftime('%I').strip('0') + ' ' + end2.strftime('%p')
            display_string += f"{start_formatted} to {end_formatted}"
            display_string += f" /\n{start2_formatted} to {end2_formatted}"
            return display_string

    def __str__(self):
        return self.name

    def get_month_int_list(self):
        int_list = []
        for month in self.month.all():
            int_list.append(month.get_int())
        return int_list

    def month_check(self):
        current_month = date.today().month
        return current_month in self.get_month_int_list()

    # can definitely be simplified!!
    def time_check(self):
        now = datetime.now()
        time_now = time(now.hour, now.minute, now.second)
        start = self.interval_start
        end = self.interval_end
        start2 = self.interval2_start
        end2 = self.interval2_end
        if start2 == end2 == time(0):
            if start < end:
                return start <= time_now <= end
            elif start > end:
                return start <= time_now or time_now <= end
            else:
                raise ValueError('interval_start and interval_end can\'t be the same!')
        else:
            if start < end or start2 < end2:
                return start <= time_now <= end or start2 <= time_now <= end2
            if start > end or start2 > end2:
                return (start <= time_now or time_now <= end) or (start2 <= time_now or time_now <= end2)

    # checks for critters available in under 12 hours (all with datetime objects)
    def time_check_soon(self):
        # checking if critter is available now (with f time_check)
        if self.time_check():
            return False

        now = datetime.now()
        # exchange 'hours' value for other intervals that are meant to signify "soon"
        now_in_12h = now + timedelta(hours=12)
        # checking if month in 12 hours is still in bug_month.all()
        if not now_in_12h.month in self.get_month_int_list():
            return False

        # converting time objects TimeFields to datetime objects
        start_dt = now_in_12h.replace(hour=self.interval_start.hour, minute=0, second=0)
        end_dt = now_in_12h.replace(hour=self.interval_end.hour, minute=self.interval_end.minute,
                                    second=self.interval_end.second)
        start2_dt = now_in_12h.replace(hour=self.interval2_start.hour, minute=0, second=0)
        end2_dt = now_in_12h.replace(hour=self.interval2_end.hour, minute=self.interval2_end.minute,
                                     second=self.interval2_end.second)
        # using same logic as in f time_check:
        if start2_dt == end2_dt == now_in_12h.replace(hour=0, minute=0, second=0):
            if start_dt < end_dt:
                return start_dt <= now_in_12h <= end_dt
            elif start_dt > end_dt:
                return start_dt <= now_in_12h or now_in_12h <= end_dt
        else:
            if start_dt < end_dt or start2_dt < end2_dt:
                return start_dt <= now_in_12h <= end_dt or start2_dt <= now_in_12h <= end2_dt
            if start_dt > end_dt or start2_dt > end2_dt:
                return (start_dt <= now_in_12h or now_in_12h <= end_dt) or \
                       (start2_dt <= now_in_12h or now_in_12h <= end2_dt)

    class Meta:
        verbose_name_plural = "DiveFish"
        ordering = ['name']

    def get_active_number(self):
        num = 0
        for critter in DiveFish.objects.all():
            if critter.month_check() and critter.time_check():
                num += 1
        return num

    def get_not_active_number(self):
        num = 0
        for critter in DiveFish.objects.all():
            if critter.month_check() and not critter.time_check() and not critter.time_check_soon():
                num += 1
        return num

    def get_soon_active_number(self):
        num = 0
        for critter in DiveFish.objects.all():
            if critter.month_check() and critter.time_check_soon():
                num += 1
        return num


class Bug(models.Model):
    LOCATION_CHOICES = [
        ('DISGBEACH', 'disguised on shorelines'),
        ('DISGTREE', 'disguised under trees'),
        ('FLY', 'flying'),
        ('FLYBPBFLOWER', 'flying near blue, purple & black flowers'),
        ('FLYFLOWER', 'flying near flowers'),
        ('LIGHT', 'flying near light sources'),
        ('TRASHTURNIP', 'flying near trash & rotten turnips'),
        ('NEARWATER', 'flying near water'),
        ('HITROCK', 'falls from rocks being hit'),
        ('BEACHROCK', 'on beach rocks'),
        ('FLOWER', 'on flowers'),
        ('PALM', 'on palm trees'),
        ('RIVERPOND', 'on rivers & ponds'),
        ('ROCKBUSH', 'on rocks & bushes'),
        ('TURNIPCANDYLOLLI', 'on rotten turnips, candy & lollipops'),
        ('GROUND', 'on ground'),
        ('STUMP', 'on tree stumps'),
        ('TREE', 'on trees'),
        ('TREEHC', 'on hardwood & cedar trees'),
        ('VILL', 'on villagers'),
        ('WFLOWER', 'on white flowers'),
        ('SNOW', 'pushing snowballs'),
        ('SHAKE', 'falls from shaking trees'),
        ('SHAKEHC', 'shaking hardwood & cedar trees'),
        ('UNDER', 'underground')
    ]

    WEATHER_CHOICES = [
        ("A", "any weather"),
        ("R", "rain only"),
        ("A-R", "any weather except rain")
    ]

    # id always like "b1", "b20", "b31"...
    id = models.CharField(primary_key=True, max_length=5, default='')
    name = models.CharField(max_length=50, unique=True)
    price = models.IntegerField(default=0)
    catches_req = models.IntegerField('b catches required', default=0)
    month = models.ManyToManyField(Month, blank=True)
    location = models.CharField(max_length=40, default='', choices=LOCATION_CHOICES, blank=True)
    weather = models.CharField(max_length=20, choices=WEATHER_CHOICES, default='A')

    # time interval for daily availability
    interval_start = models.TimeField(default=time.min)
    interval_end = models.TimeField(default=time.max)

    # time interval for bf with two available time spans
    interval2_start = models.TimeField(default=time.min)
    interval2_end = models.TimeField(default=time.min)

    def get_hours_display(self):
        start = self.interval_start
        end = self.interval_end
        start2 = self.interval2_start
        end2 = self.interval2_end
        # check if first interval includes whole day (time(0)>time(23,59,59))
        if start == time(0) and end == time(23, 59, 59):
            return "All day"
        # check if no second interval has been provided
        elif start2 == time(0) and end2 == time(0):
            start_formatted = start.strftime('%I').strip('0') + ' ' + start.strftime('%p')
            end_formatted = end.strftime('%I').strip('0') + ' ' + end.strftime('%p')
            return f"{start_formatted} to {end_formatted}"
        else:  # means: there is a second time interval for availability
            display_string = ''
            start_formatted = start.strftime('%I').strip('0') + ' ' + start.strftime('%p')
            end_formatted = end.strftime('%I').strip('0') + ' ' + end.strftime('%p')
            start2_formatted = start2.strftime('%I').strip('0') + ' ' + start2.strftime('%p')
            end2_formatted = end2.strftime('%I').strip('0') + ' ' + end2.strftime('%p')
            display_string += f"{start_formatted} to {end_formatted}"
            display_string += f" /\n{start2_formatted} to {end2_formatted}"
            return display_string

    def __str__(self):
        return self.name

    def get_month_int_list(self):
        int_list = []
        for month in self.month.all():
            int_list.append(month.get_int())
        return int_list

    def month_check(self):
        current_month = date.today().month
        return current_month in self.get_month_int_list()

    def time_check(self):
        now = datetime.now()
        time_now = time(now.hour, now.minute, now.second)
        start = self.interval_start
        end = self.interval_end
        start2 = self.interval2_start
        end2 = self.interval2_end
        if start2 == end2 == time(0):
            if start < end:
                return start <= time_now <= end
            elif start > end:
                return start <= time_now or time_now <= end
            else:
                raise ValueError('interval_start and interval_end can\'t be the same!')
        else:
            if start < end or start2 < end2:
                return start <= time_now <= end or start2 <= time_now <= end2
            if start > end or start2 > end2:
                return (start <= time_now or time_now <= end) or (start2 <= time_now or time_now <= end2)

    def time_check_soon(self):
        # checking if critter is available now (with f time_check)
        if self.time_check():
            return False

        now = datetime.now()
        # exchange 'hours' value for other intervals that are meant to signify "soon"
        now_in_12h = now + timedelta(hours=12)
        # checking if month in 12 hours is still in bug_month.all()
        if not now_in_12h.month in self.get_month_int_list():
            return False

        # converting time objects TimeFields to datetime objects
        start_dt = now_in_12h.replace(hour=self.interval_start.hour, minute=0, second=0)
        end_dt = now_in_12h.replace(hour=self.interval_end.hour, minute=self.interval_end.minute,
                                    second=self.interval_end.second)
        start2_dt = now_in_12h.replace(hour=self.interval2_start.hour, minute=0, second=0)
        end2_dt = now_in_12h.replace(hour=self.interval2_end.hour, minute=self.interval2_end.minute,
                                     second=self.interval2_end.second)
        # using same logic as in f time_check:
        if start2_dt == end2_dt == now_in_12h.replace(hour=0, minute=0, second=0):
            if start_dt < end_dt:
                return start_dt <= now_in_12h <= end_dt
            elif start_dt > end_dt:
                return start_dt <= now_in_12h or now_in_12h <= end_dt
        else:
            if start_dt < end_dt or start2_dt < end2_dt:
                return start_dt <= now_in_12h <= end_dt or start2_dt <= now_in_12h <= end2_dt
            if start_dt > end_dt or start2_dt > end2_dt:
                return (start_dt <= now_in_12h or now_in_12h <= end_dt) or \
                       (start2_dt <= now_in_12h or now_in_12h <= end2_dt)

    class Meta:
        verbose_name_plural = "Bugs"
        ordering = ['name']

    def get_active_number(self):
        num = 0
        for critter in Bug.objects.all():
            if critter.month_check() and critter.time_check():
                num += 1
        return num

    def get_not_active_number(self):
        num = 0
        for critter in Bug.objects.all():
            if critter.month_check() and not critter.time_check() and not critter.time_check_soon():
                num += 1
        return num

    def get_soon_active_number(self):
        num = 0
        for critter in Bug.objects.all():
            if critter.month_check() and critter.time_check_soon():
                num += 1
        return num


class Fish(models.Model):
    SIZE_CHOICES = [
        ('XS', 'tiny'),
        ('S', 'small'),
        ('M', 'medium'),
        ('L', 'large'),
        ('LT', 'long & thin'),
        ('XL', 'very large'),
        ('XLF', 'very large with fin'),
        ('XXL', 'huge')
    ]

    LOCATION_CHOICES = [
        ('PI', 'pier'),
        ('PO', 'pond'),
        ('R', 'river'),
        ('RC', 'river clifftop'),
        ('RM', 'river mouth'),
        ('S', 'sea')
    ]

    WEATHER_CHOICES = [
        ("A", "any weather"),
        ("R", "rain only")
    ]

    # id always like "f1", "f20", "f31"...
    id = models.CharField(primary_key=True, max_length=5, default='')
    name = models.CharField(max_length=50, unique=True)
    price = models.IntegerField(default=0)
    catches_req = models.IntegerField('f catches required', default=0)
    month = models.ManyToManyField(Month, blank=True)
    size = models.CharField(max_length=20, default='XS', choices=SIZE_CHOICES)
    location = models.CharField(max_length=40, default='', choices=LOCATION_CHOICES, blank=True)
    weather = models.CharField(max_length=20, choices=WEATHER_CHOICES, default="A")

    # time interval for daily availability
    interval_start = models.TimeField(default=time.min)
    interval_end = models.TimeField(default=time.max)

    # time interval for f with two available time spans
    interval2_start = models.TimeField(default=time.min)
    interval2_end = models.TimeField(default=time.min)

    def get_hours_display(self):
        start = self.interval_start
        end = self.interval_end
        start2 = self.interval2_start
        end2 = self.interval2_end
        # check if first interval includes whole day (time(0)>time(23,59,59))
        if start == time(0) and end == time(23, 59, 59):
            return "All day"
        # check if no second interval has been provided
        elif start2 == time(0) and end2 == time(0):
            start_formatted = start.strftime('%I').strip('0') + ' ' + start.strftime('%p')
            end_formatted = end.strftime('%I').strip('0') + ' ' + end.strftime('%p')
            return f"{start_formatted} to {end_formatted}"
        else:  # means: there is a second time interval for availability
            display_string = ''
            start_formatted = start.strftime('%I').strip('0') + ' ' + start.strftime('%p')
            end_formatted = end.strftime('%I').strip('0') + ' ' + end.strftime('%p')
            start2_formatted = start2.strftime('%I').strip('0') + ' ' + start2.strftime('%p')
            end2_formatted = end2.strftime('%I').strip('0') + ' ' + end2.strftime('%p')
            display_string += f"{start_formatted} to {end_formatted}"
            display_string += f" /\n{start2_formatted} to {end2_formatted}"
            return display_string

    def __str__(self):
        return self.name

    def get_month_int_list(self):
        int_list = []
        for month in self.month.all():
            int_list.append(month.get_int())
        return int_list

    def month_check(self):
        current_month = date.today().month
        return current_month in self.get_month_int_list()

    def time_check(self):
        now = datetime.now()
        time_now = time(now.hour, now.minute, now.second)
        start = self.interval_start
        end = self.interval_end
        start2 = self.interval2_start
        end2 = self.interval2_end
        if start2 == end2 == 0:
            if start < end:
                return start <= time_now <= end
            elif start > end:
                return start <= time_now or time_now <= end
            else:
                raise ValueError('interval_start and interval_end can\'t be the same!')
        else:
            if start < end or start2 < end2:
                return start <= time_now <= end or start2 <= time_now <= end2
            if start > end or start2 > end2:
                return (start <= time_now or time_now <= end) or (start2 <= time_now or time_now <= end2)

    def time_check_soon(self):
        # checking if critter is available now (with f time_check)
        if self.time_check():
            return False

        now = datetime.now()
        # exchange 'hours' value for other intervals that are meant to signify "soon"
        now_in_12h = now + timedelta(hours=12)
        # checking if month in 12 hours is still in bug_month.all()
        if not now_in_12h.month in self.get_month_int_list():
            return False

        # converting time objects TimeFields to datetime objects
        start_dt = now_in_12h.replace(hour=self.interval_start.hour, minute=0, second=0)
        end_dt = now_in_12h.replace(hour=self.interval_end.hour, minute=self.interval_end.minute,
                                    second=self.interval_end.second)
        start2_dt = now_in_12h.replace(hour=self.interval2_start.hour, minute=0, second=0)
        end2_dt = now_in_12h.replace(hour=self.interval2_end.hour, minute=self.interval2_end.minute,
                                     second=self.interval2_end.second)
        # using same logic as in f time_check:
        if start2_dt == end2_dt == now_in_12h.replace(hour=0, minute=0, second=0):
            if start_dt < end_dt:
                return start_dt <= now_in_12h <= end_dt
            elif start_dt > end_dt:
                return start_dt <= now_in_12h or now_in_12h <= end_dt
        else:
            if start_dt < end_dt or start2_dt < end2_dt:
                return start_dt <= now_in_12h <= end_dt or start2_dt <= now_in_12h <= end2_dt
            if start_dt > end_dt or start2_dt > end2_dt:
                return (start_dt <= now_in_12h or now_in_12h <= end_dt) or \
                       (start2_dt <= now_in_12h or now_in_12h <= end2_dt)


    def get_active_number(self):
        num = 0
        for critter in Fish.objects.all():
            if critter.month_check() and critter.time_check():
                num += 1
        return num

    def get_not_active_number(self):
        num = 0
        for critter in Fish.objects.all():
            if critter.month_check() and not critter.time_check() and not critter.time_check_soon():
                num += 1
        return num

    def get_soon_active_number(self):
        num = 0
        for critter in Fish.objects.all():
            if critter.month_check() and critter.time_check_soon():
                num += 1
        return num

    class Meta:
        verbose_name_plural = "Fish"
        ordering = ['name']