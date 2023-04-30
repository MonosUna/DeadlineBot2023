import datetime

def parser(string: str):
    lst = []

    word = string[0: string.find('.')]
    lst.append(int(word))
    string = string[string.find('.') + 1:]

    word = string[0: string.find('.')]
    lst.append(int(word))
    string = string[string.find('.') + 1:]

    word = string[0: string.find(' ')]
    lst.append(int(word))
    string = string[string.find(' ') + 1:]

    word = string[0: string.find(':')]
    lst.append(int(word))
    string = string[string.find(':') + 1:]

    lst.append(int(string))

    return lst


class Deadline:
    def __init__(self, date: str, name: str, priority: int, difficult: int):
        lst = parser(date)
        self.date = datetime.datetime(lst[0], lst[1], lst[2], lst[3], lst[4])
        self.name = name
        self.priority = priority
        self.difficult = difficult

    def hours_to_dl(self):
        now = datetime.datetime.now()
        delta = self.date - now
        hours = int(delta.total_seconds()) // 3600
        return hours
