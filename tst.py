import random

a = {'а': 8, 'б': 2, 'в': 4, 'г': 2, 'д': 4, 'е': 8, 'ё': 1, 'ж': 1, 'з': 2, 'и': 5, 'й': 1, 'к': 4, 'л': 4, 'м': 3, 'н': 5, 'о': 10, 'п': 4, 'р': 5, 'с': 5, 'т': 5, 'у': 4, 'ф': 1, 'х': 2, 'ц': 1, 'ч': 2, 'ш': 1, 'щ': 1, 'ъ': 1, 'ь': 2, 'ы': 2, 'э': 1, 'ю': 1, 'я': 2}

b = ["ф", "м", "ф", "а", "а"]

def change_letters(a, b):
    new_b = random.choices(list(a.keys()), k=len(b))
    new_let = ''


