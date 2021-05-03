from telegram import KeyboardButton


class KEYBOARD:
    def __init__(self, number_row: int):
        self.num_row = number_row
        self.keyboard = [[] for i in range(self.num_row)]

    def add_button(self, text, row, location=False) -> None:
        but = KeyboardButton(text,request_location=location)
        self.keyboard[row].append(but)

# +++
start_k = KEYBOARD(1)
start_k.add_button("\U0001F680 Let's go", 0)
# +++
action_choice_k = KEYBOARD(2)
action_choice_k.add_button("\U0001F3E2 City",0)
action_choice_k.add_button("\U0001F4E1 Location", 0, location=True)
action_choice_k.add_button("\U00002699 Settings", 1)
# +++
city_choice_k = KEYBOARD(2)
city_choice_k.add_button("\U0001F4DD File city", 0)
city_choice_k.add_button("\U0001F50E Find city", 0)
city_choice_k.add_button("\U000021A9 Back", 1)
# +++
weather_choice_k = KEYBOARD(1)
weather_choice_k.add_button("\U000025B6 Now", 0)
weather_choice_k.add_button("\U000023ED Forecast", 0)
# +++
settings_choice_k = KEYBOARD(2)
settings_choice_k.add_button("\U0000267B Change city", 0)
settings_choice_k.add_button("\U00002709 Send message", 0)
settings_choice_k.add_button("\U000021A9 Back", 1)
# ---
change_city_choice_k = KEYBOARD(2)
change_city_choice_k.add_button("\U00002328 Use city's name", 0)
change_city_choice_k.add_button("\U0001F6F0 Use location point", 0, location=True)
change_city_choice_k.add_button("\U000021A9 Back", 1)