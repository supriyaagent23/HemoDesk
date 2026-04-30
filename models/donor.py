class Donor:
    def __init__(self, name, age, blood_type, phone, gender="", last_donation=None, id=None, total_donations=0):
        self.id = id
        self.name = name
        self.age = age
        self.blood_type = blood_type
        self.phone = phone
        self.gender = gender  
        self.last_donation = last_donation
        self.total_donations = total_donations