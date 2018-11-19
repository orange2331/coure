import pandas as pd
import re
import requests
from tqdm import tqdm_notebook
import phonenumbers


class PhoneValidator:
    def validate(self, phone_number):
        try:
            phone = phonenumbers.parse(phone_number, 'RU')
        except phonenumbers.NumberParseException:
            return None

        if phonenumbers.is_valid_number(phone):
            return ''.join(
                [i for i in phonenumbers.format_number(phone, phonenumbers.PhoneNumberFormat.NATIONAL) if i.isdigit()])

        else:
            return None


class EmailValidator:
    def validate(self, email):
        try:
            pattern = re.compile(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")
            return re.match(pattern, email).group()
        except AttributeError:
            return None


class CityValidator:
    def validate(self, city):
        # компилируем регулярное выражение
        s = city.lower()
        s = s.strip()
        s = s.replace(".", "")
        s = s.replace(',', '')
        pattern = re.compile(r"й")
        pattern2 = re.compile(r"ё")
        pattern3 = re.compile(r"пгт |пос |р?п |г |с |д |станица| раион|р н | область|краи|республика |кр |мкр |ао| обл")

        city_clean = re.sub(pattern, 'и', s)
        city_clean2 = re.sub(pattern2, 'е', city_clean)
        city_clean3 = re.sub(pattern3, "", city_clean2)

        return city_clean3
 def distance(city_a, city_b):
        n, m = len(city_a), len(city_b)
        if n > m:
            # Make sure n <= m, to use O(min(n,m)) space
            city_a, city_b = city_b, city_a
            n, m = m, n

        current_row = range(n + 1)  # Keep current and previous row, not entire matrix
        for i in range(1, m + 1):
            previous_row, current_row = current_row, [i] + [0] * n
            for j in range(1, n + 1):
                add, delete, change = previous_row[j] + 1, current_row[j - 1] + 1, previous_row[j - 1]
                if city_a[j - 1] != city_b[i - 1]:
                    change += 1
                current_row[j] = min(add, delete, change)

        return current_row[n]

def get_id(city_name, max_distance):
        for key in d:
            valid = CityValidator()
            valid_key = valid.validate(key)
            if distance(city_name, valid_key) <= max_distance:
                return d[key]
        else:
            return None

BASE_URL = "https://api.hh.ru/areas"
requests.get(BASE_URL)
s = requests.Session()
response = s.get(BASE_URL)
city_tree = response.json()e

d = {}


def flat_cities(name, city_tree):
    d[city_tree["name"]] = city_tree["id"]
    if len(city_tree["areas"]) > 0:
        for item in city_tree["areas"]:
            flat_cities(name, item)


for cont in city_tree:
    flat_cities("Московская область", cont)

data = pd.read_csv("CRM_sample.tsv", sep='\t')
data.head()

filtred_data=data[(data["Email"].notnull() | data["HomePhone"].notnull()) & data['City'].notnull()]
filtred_data

all_phones=[HomePhone for HomePhone in filtred_data['HomePhone']]

validator = PhoneValidator()
valid_phones = []
for i in all_phones:
    if isinstance(i, str):
        new_phone=validator.validate(i)
        valid_phones.append(new_phone)
    else:
        valid_phones.append(None)

filtred_data['phone_validation']=pd.Series(valid_phones)

all_emails =filtred_data['Email'].values
all_emails
validator_mail = EmailValidator()
valid_mails = []
for i in all_emails:
    if isinstance(i, str):
        new_mail=validator_mail.validate(i)
        valid_mails.append(new_mail)
    else:
        valid_mails.append(None)
filtred_data['validation_email']=pd.Series(valid_mails)
all_cities = data['City'].values
cities_id=[]
for i in all_cities:
    if isinstance(i, str):
        city_id=get_id(i,1)
        cities_id.append(city_id)
data['city_id']=pd.Series(cities_id)
offers = pd.read_csv("offers.tsv", sep='\t')
offers

all_offer_cities = offers['Place'].values
offer_city_id=[]
for i in all_offer_cities:
    if isinstance(i, str):
        new_offer_city_id=get_id(i,1)
        offer_city_id.append(new_offer_city_id)

offers['city_id']=pd.Series(offer_city_id)
offers

data[data['city_id'].notnull()]
data

off=offers[['Text','city_id']]
off[off['city_id'].notnull()]
off

data["city_id"] = data["city_id"].astype(int)
off['city_id']=off['city_id'].astype(int)

data.merge(off, on="city_id", how="inner")
