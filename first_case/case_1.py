import pandas as pd
import re
import requests
import phonenumbers


class PhoneValidator:
    @staticmethod
    def validate(phone_number):
        try:
            phone = phonenumbers.parse(phone_number, 'RU')
        except phonenumbers.NumberParseException:
            return None

        if phonenumbers.is_valid_number(phone):
            return ''.join(
                [i for n in phonenumbers.format_number(phone, phonenumbers.PhoneNumberFormat.NATIONAL) if n.isdigit()])

        else:
            return None


class EmailValidator:
    @staticmethod
    def validate(email):
        try:
            pattern = re.compile(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")
            return re.match(pattern, email).group()
        except AttributeError:
            return None


class CityValidator:
    @staticmethod
    def validate(city):
        # компилируем регулярное выражение
        l = city.lower()
        l = l.strip()
        l = l.replace(".", "")
        l = l.replace(',', '')
        pattern = re.compile(r"й")
        pattern2 = re.compile(r"ё")
        pattern3 = re.compile(r"пгт |пос |р?п |г |с |д |станица| раион|р н | область|краи|республика |кр |мкр |ао| обл")

        city_clean = re.sub(pattern, 'и', l)
        city_clean2 = re.sub(pattern2, 'е', city_clean)
        city_clean3 = re.sub(pattern3, "", city_clean2)
        return city_clean3


def distance(city_a, city_b):  # расстояние Левинштейна
    n, m = len(city_a), len(city_b)
    if n > m:
        # Make sure n <= m, to use O(min(n,m)) space
        city_a, city_b = city_b, city_a
        n, m = m, n

    current_row = range(n + 1)  # Keep current and previous row, not entire matrix
    for n in range(1, m + 1):
        previous_row, current_row = current_row, [n] + [0] * n
        for j in range(1, n + 1):
            add, delete, change = previous_row[j] + 1, current_row[j - 1] + 1, previous_row[j - 1]
            if city_a[j - 1] != city_b[n - 1]:
                change += 1
            current_row[j] = min(add, delete, change)
    return current_row[n]


def get_id(city_name, max_distance):  # получение id города из списка
    for key in city_dict:
        valid = CityValidator()
        valid_key = valid.validate(key)
        if distance(city_name, valid_key) <= max_distance:
            return city_dict[key]
    else:
        return None


def flat_cities(name, city_tree1):  # преобразование в плоский словарь
    city_dict[city_tree1["name"]] = city_tree1["id"]
    if len(city_tree1["areas"]) > 0:
        for item in city_tree1["areas"]:
            flat_cities(name, item)


if __name__ == "__main__":
    BASE_URL = "https://api.hh.ru/areas"
    requests.get(BASE_URL)
    s = requests.Session()
    response = s.get(BASE_URL)
    city_tree = response.json()

    city_dict = {}

    for cont in city_tree:
        flat_cities("Московская область", cont)

    data = pd.read_csv("CRM_sample.tsv", sep='\t')

    filtred_data = data[(data["Email"].notnull() | data["HomePhone"].notnull()) & data['City'].notnull()]
    all_phones = [HomePhone for HomePhone in filtred_data['HomePhone']]
    validator = PhoneValidator()
    valid_phones = []

    for i in all_phones:
        if isinstance(i, str):
            new_phone = validator.validate(i)
            valid_phones.append(new_phone)
        else:
            valid_phones.append(None)

    filtred_data['phone_validation'] = pd.Series(valid_phones)

    all_emails = filtred_data['Email'].values

    validator_mail = EmailValidator()
    valid_mails = []
    for i in all_emails:
        if isinstance(i, str):
            new_mail = validator_mail.validate(i)
            valid_mails.append(new_mail)
        else:
            valid_mails.append(None)

    filtred_data['validation_email'] = pd.Series(valid_mails)
    all_cities = data['City'].values
    cities_id = []
    for i in all_cities:
        if isinstance(i, str):
            city_id = get_id(i, 1)
            cities_id.append(city_id)

    data['city_id'] = pd.Series(cities_id)

    offers = pd.read_csv("offers.tsv", sep='\t')
    all_offer_cities = offers['Place'].values

    offer_city_id = []
    for i in all_offer_cities:
        if isinstance(i, str):
            new_offer_city_id = get_id(i, 1)
            offer_city_id.append(new_offer_city_id)

    offers['city_id'] = pd.Series(offer_city_id)
    data_filter = data[data['city_id'].notnull()]
    off = offers[['Text', 'city_id']]
    off_filter = off[off['city_id'].notnull()]
    final_file = data_filter.merge(off_filter, on="city_id", how="inner")
    print(final_file)
