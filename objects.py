class EDTTime:
    def __init__(self, hour, minute):
        self.hour = hour
        self.minute = minute

    def __str__(self):
        return f"{self.hour}:{self.minute}"
    
    def formatted_time(self):
        return f"{self.hour:02d}:{self.minute:02d}:00"

class EDTDate:
    def __init__(self, day, month, year):
        self.day = day
        self.month = month
        self.year = year

    def __str__(self):
        return f"{self.day}/{self.month}/{self.year}"
    
    def formatted_date(self):
        return f"{self.year}-{self.month:02d}-{self.day:02d}"

class Cours:
    name: str
    date: EDTDate
    start: EDTTime
    end: EDTTime
    room: str
    teacher: str
    class_name: str
    def __init__(self, name, date, start, end, room, teacher, class_name):
        self.name = name
        self.date = date
        self.start = start
        self.end = end
        self.room = room
        self.teacher = teacher
        self.class_name = class_name

    def __str__(self):
        return f"{self.name} | {self.date} {self.start} - {self.end} | {self.room} | {self.teacher} | {self.class_name}"
    
    def json(self):
        return {
            "name": self.name,
            "date": self.date.formatted_date(),
            "start": self.start.formatted_time(),
            "end": self.end.formatted_time(),
            "room": self.room,
            "teacher": self.teacher,
            "class_name": self.class_name
        }
    
class Day:
    name: str
    cours: list[Cours]
    def __init__(self, name, cours):
        self.name = name
        self.cours = cours

    def __str__(self):
        return f"{self.name} | {self.cours}"
    
    def json(self):
        return {
            "name": self.name,
            "cours": [cours.json() for cours in self.cours]
        }
    
class Week:
    days: list[Day]
    def __init__(self, days):
        self.days = days

    def __str__(self):
        return f"{self.days}"