from telegram import KeyboardButton


class KEYBOARD:
    def __init__(self, number_row: int):
        self.num_row = number_row
        self.keyboard = [[] for i in range(self.num_row)]

    def add_button(self, text, row, location=False) -> None:
        but = KeyboardButton(text, request_location=location)
        self.keyboard[row].append(but)


# +++
start_k = KEYBOARD(1)
start_k.add_button("\U000025B6 Let's go", 0)
# +++
action_choice_k = KEYBOARD(2)
action_choice_k.add_button("\U0001F436 VK", 0)
action_choice_k.add_button("\U00002699 Settings", 1)
# +++
vk_choice_k = KEYBOARD(2)
vk_choice_k.add_button("\U0001F4BD Person-id music", 0)
vk_choice_k.add_button("\U0001F50D Find music", 0)
vk_choice_k.add_button("\U000021A9 Back", 1)
# +++
settings_choice_k = KEYBOARD(2)
settings_choice_k.add_button("\U00002709 Send message", 0)
settings_choice_k.add_button("\U000021A9 Back", 1)
