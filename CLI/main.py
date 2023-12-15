from datetime import datetime, timedelta
from collections import UserDict, defaultdict

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    pass


class Phone(Field):
    def __init__(self, value):
        super().__init__(value)

        if not str(value).isdigit() or len(str(value)) != 10:
            raise ValueError("Invalid phone number format. Must be 10 digits.")


class Birthday:
    def __init__(self, date_str):
        try:
            self.date = datetime.strptime(date_str, "%d.%m.%Y").date()
        except ValueError:
            raise ValueError("Invalid date format. Please use DD.MM.YYYY")

    def __str__(self):
        return self.date.strftime("%d.%m.%Y")


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def add_birthday(self, date_str):
        self.birthday = Birthday(date_str)

    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if p.value != phone]

    def edit_phone(self, old_phone, new_phone):
        self.remove_phone(old_phone)
        self.add_phone(new_phone)

    def find_phone(self, phone):
        return next((p for p in self.phones if p.value == phone), None)

    def __str__(self):
        phones = ', '.join(str(p) for p in self.phones)
        birthday = f", Birthday: {self.birthday}" if self.birthday else ""
        return f"Contact name: {self.name}, phones: {phones}{birthday}"


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def get_birthdays_per_week(self):
        birthdays = defaultdict(list)
        today = datetime.today().date()

        for record in self.data.values():
            birthday = record.birthday.date if record.birthday else None

            if birthday:
                birthday_this_year = birthday.replace(year=today.year)
                if birthday_this_year < today:
                    birthday_this_year = birthday_this_year.replace(year=today.year + 1)

                delta_days = (birthday_this_year - today).days

                if delta_days < 7:
                    day_of_week = (today + timedelta(days=delta_days)).strftime("%A")
                    if day_of_week in ["Saturday", "Sunday"]:
                        day_of_week = "Monday"
                    birthdays[day_of_week].append(record.name.value)

        return birthdays


class BotHandler:
    def __init__(self):
        self.book = AddressBook()

    def handle_add(self, name, phone):
        record = Record(name)
        record.add_phone(phone)
        self.book.add_record(record)
        return f"Contact {name} added with phone {phone}."

    def handle_change(self, name, new_phone):
        record = self.book.find(name)
        if record:
            old_phone = record.phones[0].value
            record.edit_phone(old_phone, new_phone)
            return f"Phone number for {name} changed to {new_phone}."
        else:
            return f"Contact {name} not found."

    def handle_phone(self, name):
        record = self.book.find(name)
        if record:
            return f"Phone number for {name}: {record.phones[0]}."
        else:
            return f"Contact {name} not found."

    def handle_all(self):
        if not self.book.data:
            return "Address book is empty."
        return "\n".join(str(record) for record in self.book.data.values())

    def add_birthday(self, name, date_str):
        record = self.book.find(name)
        if record:
            try:
                record.add_birthday(date_str)
                return f"Birthday added for {name}."
            except ValueError as e:
                return str(e)
        else:
            return f"Contact {name} not found."

    def show_birthday(self, name):
        record = self.book.find(name)
        if record and record.birthday:
            return f"{name}'s birthday: {record.birthday}."
        elif record:
            return f"{name} has no birthday recorded."
        else:
            return f"Contact {name} not found."

    def birthdays(self):
        birthdays = self.book.get_birthdays_per_week()
        if birthdays:
            return "\n".join([f"{day}: {', '.join(names)}" for day, names in birthdays.items()])
        else:
            return "No birthdays in the upcoming week."

    def hello(self):
        return "Hello!"

    def lose(self):
        return "Closing program."


if __name__ == "__main__":
    bot = BotHandler()

    while True:
        command = input("Enter a command: ")
        
        if command.startswith("add "):
            _, name, phone = command.split(" ", 2)
            result = bot.handle_add(name, phone)

        elif command.startswith("change "):
            _, name, new_phone = command.split(" ", 2)
            result = bot.handle_change(name, new_phone)

        elif command.startswith("phone "):
            _, name = command.split(" ", 1)
            result = bot.handle_phone(name)

        elif command == "all":
            result = bot.handle_all()

        elif command.startswith("add-birthday "):
            _, name, date_str = command.split(" ", 2)
            result = bot.add_birthday(name, date_str)

        elif command.startswith("show-birthday "):
            _, name = command.split(" ", 1)
            result = bot.show_birthday(name)

        elif command == "birthdays":
            result = bot.birthdays()

        elif command == "hello":
            result = bot.hello()

        elif command == "close" or command == "exit":
            result = bot.close()
            break

        else:
            result = "Invalid command. Please try again."

        print(result)
