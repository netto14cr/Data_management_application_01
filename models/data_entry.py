# models/data_entry.py

class DataEntry:
    def __init__(self, name, age, email, phone=None, address=None):
        self.name = name
        self.age = age
        self.email = email
        self.phone = phone
        self.address = address

    def is_valid(self):
        if not self.name or not self.age or not self.email:
            return False
        if not isinstance(self.age, int) or self.age <= 0:
            return False
        return True
