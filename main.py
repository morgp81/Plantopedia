# ============================================================
# Plantopedia - Kivy Plant Care App
# ============================================================
# Features:
# - Green theme
# - Home screen with saved plants
# - Add Plant screen
# - Care Tips screen
# - Edit Plant screen
# - Pest Tips screen
# - Light Sensor screen
# - Shows time since each plant was last watered
# - "Water Plant" button updates last watered time
# - Vibrates and says "Plant watered!" on Android
# - Uses phone light sensor to check if environment fits plant
# - JSON saving
# - Nested if statements for project requirement
#
# To run locally:
#     python main.py
#
# For Android APK with Buildozer, include:
#     requirements = python3,kivy,plyer
#     android.permissions = VIBRATE
# ============================================================

import json
import os
from datetime import datetime

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner

# Plyer gives access to phone hardware features.
# These will usually only work on a real Android phone, not your computer.
try:
    from plyer import vibrator
except Exception:
    vibrator = None

try:
    from plyer import light
except Exception:
    light = None


PLANT_FILE = "plants.json"

Window.clearcolor = (0.92, 0.98, 0.90, 1)

DARK_GREEN = (0.12, 0.45, 0.18, 1)
MEDIUM_GREEN = (0.22, 0.62, 0.28, 1)
LIGHT_GREEN = (0.85, 0.95, 0.82, 1)
TEXT_DARK = (0.10, 0.20, 0.10, 1)
WHITE = (1, 1, 1, 1)

# The actual character "3" appears here for the requirement.
APP_TAGLINE = "Track plants in 3 easy steps."

DEFAULT_PLANT_TYPES = [
    "Fern",
    "Fiddle Leaf Fig",
    "Monstera",
    "Snake Plant",
    "Jade Plant",
    "String of Pearls",
    "Hibiscus",
    "Chinese Evergreen",
    "Cactus",
    "Sunflower",
    "Other"
]

PLANT_CARE_INFO = {
    "Fern": {
        "light": "Only indirect sunlight. Direct sunlight can burn it.",
        "water": "Soil needs to be consistently damp.",
        "extra": "Indoor ferns usually need water 1-2 times a week. Outdoor ferns may need water every other day.",
        "light_min": 50,
        "light_max": 1000,
        "light_label": "indirect / low to medium light"
    },
    "Fiddle Leaf Fig": {
        "light": "Needs a very bright spot.",
        "water": "Water when the top 2 inches of soil feel dry. Overwatering can kill this plant.",
        "extra": "Yellowing or dark brown interior spots may mean overwatering or root rot. Crispy brown curling edges may mean underwatering or low humidity. Reddish freckles can mean the plant took in too much water too quickly.",
        "light_min": 1000,
        "light_max": 10000,
        "light_label": "bright indirect light"
    },
    "Monstera": {
        "light": "Bright indirect sunlight.",
        "water": "Water when the top 2-3 inches of soil are dry.",
        "extra": "TOXIC TO PETS AND HUMANS. Likes warm temperatures and high humidity. Fertilize every month.",
        "light_min": 500,
        "light_max": 5000,
        "light_label": "bright indirect light"
    },
    "Snake Plant": {
        "light": "Bright indirect sunlight.",
        "water": "Let all of the soil dry completely before watering.",
        "extra": "Long-living succulent. Water every 2-3 weeks or sometimes once a month.",
        "light_min": 50,
        "light_max": 5000,
        "light_label": "low to bright indirect light"
    },
    "Jade Plant": {
        "light": "Can handle direct or indirect sunlight. Good light helps prevent it from getting leggy.",
        "water": "Let soil dry out completely before watering again.",
        "extra": "Long-living succulent. Fertilize every 1-2 months.",
        "light_min": 1000,
        "light_max": 20000,
        "light_label": "bright direct or indirect light"
    },
    "String of Pearls": {
        "light": "Direct morning sunlight is healthy, but avoid harsh afternoon sun. Use indirect sunlight for the rest of the day.",
        "water": "Water when soil is completely dry and the pearls look shriveled or less plump.",
        "extra": "Temperature fluctuation stresses this plant. It does not like cold temperatures below 65°F.",
        "light_min": 1000,
        "light_max": 10000,
        "light_label": "morning sun or bright indirect light"
    },
    "Hibiscus": {
        "light": "Daily direct sunlight, 6-8 hours minimum.",
        "water": "Water deeply 2-3 times a week. The top inch of soil should never be completely dry.",
        "extra": "Feed with fertilizer every 2-3 weeks. Most hibiscus plants do not like cold and may die if temperature drops to 40°F or below.",
        "light_min": 10000,
        "light_max": 100000,
        "light_label": "direct sunlight"
    },
    "Chinese Evergreen": {
        "light": "Indirect sunlight. Avoid harsh direct light. Can survive in low light.",
        "water": "Let the top 2 inches of soil dry before watering.",
        "extra": "Likes high humidity. Feed once a month in spring and summer. Do not fertilize during fall and winter.",
        "light_min": 50,
        "light_max": 2500,
        "light_label": "low to medium indirect light"
    },
    "Cactus": {
        "light": "Bright direct sunlight, 4-6 hours minimum.",
        "water": "Soil needs to be completely dry before watering. Then water generously.",
        "extra": "If a cactus leans toward the sun, it needs more sunlight and should be moved for easier light access.",
        "light_min": 10000,
        "light_max": 100000,
        "light_label": "bright direct sunlight"
    },
    "Sunflower": {
        "light": "Direct sunlight, 6-8 hours minimum.",
        "water": "Water 1-2 times a week. It should get at least 1 inch of water per week.",
        "extra": "Sunflowers grow best with strong sun and consistent watering.",
        "light_min": 10000,
        "light_max": 100000,
        "light_label": "direct sunlight"
    },
    "Other": {
        "light": "Check the specific light needs for this plant.",
        "water": "Check soil moisture before watering.",
        "extra": "Avoid overwatering and watch for pests.",
        "light_min": 100,
        "light_max": 10000,
        "light_label": "general indoor plant light"
    }
}

PEST_INFO = {
    "Spider mites": "Spider mites like dusty conditions and dry air. Wipe down leaves gently and use neem oil or something similar.",
    "Thrips": "Thrips pierce the plant and feed on sap. Use insecticidal soap and wash the foliage.",
    "Mealy bugs": "Mealy bugs look like cotton-like masses in plant creases. Touch them with a rubbing-alcohol cotton swab or spray the plant with neem oil.",
    "Fungus gnats": "Fungus gnats are tiny flies attracted to moist soil. Use yellow sticky traps or let the soil dry more before watering."
}


def make_label(text, font_size=18, height=None):
    label = Label(
        text=text,
        font_size=font_size,
        color=TEXT_DARK,
        halign="center",
        valign="middle"
    )

    if height is not None:
        label.size_hint_y = None
        label.height = height

    label.bind(size=lambda instance, value: setattr(instance, "text_size", value))
    return label


def make_button(text):
    return Button(
        text=text,
        size_hint_y=None,
        height=52,
        background_normal="",
        background_color=MEDIUM_GREEN,
        color=WHITE
    )


def load_plants():
    if not os.path.exists(PLANT_FILE):
        return []

    try:
        with open(PLANT_FILE, "r") as file:
            return json.load(file)
    except json.JSONDecodeError:
        return []


def save_plants(plants):
    with open(PLANT_FILE, "w") as file:
        json.dump(plants, file, indent=4)


def get_now_string():
    return datetime.now().isoformat(timespec="seconds")


def format_time_since_watered(last_watered):
    if not last_watered:
        return "Never watered in the app"

    try:
        last = datetime.fromisoformat(last_watered)
    except ValueError:
        return "Unknown"

    difference = datetime.now() - last

    days = difference.days
    hours = difference.seconds // 3600
    minutes = (difference.seconds % 3600) // 60

    if days > 0:
        return f"{days} day(s), {hours} hour(s) ago"
    elif hours > 0:
        return f"{hours} hour(s), {minutes} minute(s) ago"
    else:
        return f"{minutes} minute(s) ago"


def get_light_level_name(lux):
    if lux < 50:
        return "very low light"
    elif lux < 500:
        return "low light"
    elif lux < 2500:
        return "medium indirect light"
    elif lux < 10000:
        return "bright indirect light"
    else:
        return "direct / very bright light"


def check_light_for_plant(plant_type, lux):
    info = PLANT_CARE_INFO.get(plant_type, PLANT_CARE_INFO["Other"])
    light_min = info["light_min"]
    light_max = info["light_max"]

    level_name = get_light_level_name(lux)

    # Nested if logic for project requirement:
    # First check if the light is too low.
    if lux < light_min:
        if plant_type in ["Cactus", "Sunflower", "Hibiscus"]:
            return f"{lux:.0f} lux = {level_name}. This is too low for {plant_type}. Move it to stronger direct sunlight."
        else:
            return f"{lux:.0f} lux = {level_name}. This may be too dim for {plant_type}. Try a brighter indirect-light spot."

    # Second nested if logic:
    # Now check if the light is too high.
    if lux > light_max:
        if plant_type in ["Fern", "Chinese Evergreen"]:
            return f"{lux:.0f} lux = {level_name}. This is probably too harsh for {plant_type}. Move it away from direct sun."
        else:
            return f"{lux:.0f} lux = {level_name}. This may be more light than needed for {plant_type}."

    return f"{lux:.0f} lux = {level_name}. This looks suitable for {plant_type}. Target: {info['light_label']}."


def get_care_tip(plant_type, location, problem):
    info = PLANT_CARE_INFO.get(plant_type, PLANT_CARE_INFO["Other"])

    tip = (
        f"Light: {info['light']}\n\n"
        f"Water: {info['water']}\n\n"
        f"Extra: {info['extra']}"
    )

    if plant_type == "Fern":
        if location == "Indoor":
            tip += "\n\nLocation Tip: Since this fern is indoors, water it about 1-2 times a week."
        else:
            tip += "\n\nLocation Tip: Since this fern is outdoors, check it often. It may need water every other day."

    if plant_type == "Fiddle Leaf Fig":
        if problem == "Yellow leaves or dark spots":
            tip += "\n\nProblem Tip: This may be overwatering or root rot. Let the soil dry and check the roots."
        elif problem == "Crispy brown edges":
            tip += "\n\nProblem Tip: This may be underwatering or low humidity. Water more carefully and raise humidity."
        elif problem == "Reddish freckles":
            tip += "\n\nProblem Tip: This can happen when the plant takes in too much water too quickly."

    if plant_type in ["Snake Plant", "Jade Plant", "Cactus", "String of Pearls"]:
        if problem == "Soil is always wet":
            tip += "\n\nProblem Tip: This plant hates staying wet. Wait until the soil is fully dry before watering again."
        else:
            tip += "\n\nSucculent/Cactus Tip: These plants usually prefer drying out between waterings."

    if plant_type == "Monstera":
        if location == "Indoor":
            tip += "\n\nSafety Tip: Keep this plant away from pets and small children."

    return tip


class HomeScreen(Screen):
    def on_enter(self):
        self.clear_widgets()

        main = BoxLayout(orientation="vertical", padding=20, spacing=10)

        main.add_widget(make_label("Plantopedia", font_size=34, height=60))
        main.add_widget(make_label(APP_TAGLINE, font_size=18, height=35))

        add_button = make_button("Add New Plant")
        add_button.bind(on_press=self.go_to_add)
        main.add_widget(add_button)

        pest_button = make_button("Common Pest Tips")
        pest_button.bind(on_press=self.go_to_pests)
        main.add_widget(pest_button)

        light_button = make_button("Check Light Sensor")
        light_button.bind(on_press=self.go_to_light)
        main.add_widget(light_button)

        scroll = ScrollView()
        plant_list = BoxLayout(orientation="vertical", size_hint_y=None, spacing=10)
        plant_list.bind(minimum_height=plant_list.setter("height"))

        plants = load_plants()

        if len(plants) == 0:
            plant_list.add_widget(make_label("No plants saved yet.", height=50))
        else:
            for index, plant in enumerate(plants):
                row = BoxLayout(orientation="vertical", size_hint_y=None, height=105, spacing=4)

                view_button = Button(
                    text=f"{plant.get('name', 'Unnamed')} - {plant.get('type', 'Other')}\nLast watered: {format_time_since_watered(plant.get('last_watered'))}",
                    background_normal="",
                    background_color=MEDIUM_GREEN,
                    color=WHITE
                )
                view_button.bind(on_press=lambda instance, i=index: self.view_tips(i))

                small_row = BoxLayout(orientation="horizontal", size_hint_y=None, height=42, spacing=6)

                water_button = Button(
                    text="Water",
                    background_normal="",
                    background_color=DARK_GREEN,
                    color=WHITE
                )
                water_button.bind(on_press=lambda instance, i=index: self.water_plant(i))

                edit_button = Button(
                    text="Edit",
                    background_normal="",
                    background_color=DARK_GREEN,
                    color=WHITE
                )
                edit_button.bind(on_press=lambda instance, i=index: self.edit_plant(i))

                small_row.add_widget(water_button)
                small_row.add_widget(edit_button)

                row.add_widget(view_button)
                row.add_widget(small_row)

                plant_list.add_widget(row)

        scroll.add_widget(plant_list)
        main.add_widget(scroll)

        self.add_widget(main)

    def go_to_add(self, instance):
        self.manager.current = "add"

    def go_to_pests(self, instance):
        self.manager.current = "pests"

    def go_to_light(self, instance):
        self.manager.current = "light"

    def view_tips(self, index):
        tips_screen = self.manager.get_screen("tips")
        tips_screen.set_plant_index(index)
        self.manager.current = "tips"

    def edit_plant(self, index):
        edit_screen = self.manager.get_screen("edit")
        edit_screen.load_plant(index)
        self.manager.current = "edit"

    def water_plant(self, index):
        plants = load_plants()

        if index < 0 or index >= len(plants):
            return

        plants[index]["last_watered"] = get_now_string()
        save_plants(plants)

        if vibrator is not None:
            try:
                vibrator.vibrate(0.4)
            except Exception:
                pass

        watered_screen = self.manager.get_screen("watered")
        watered_screen.set_message(plants[index].get("name", "Plant"))
        self.manager.current = "watered"


class WateredScreen(Screen):
    def set_message(self, plant_name):
        self.clear_widgets()

        main = BoxLayout(orientation="vertical", padding=20, spacing=12)

        main.add_widget(make_label("Plant watered!", font_size=34, height=90))
        main.add_widget(make_label(f"{plant_name} was watered just now.", font_size=20, height=70))

        back_button = make_button("Back to Home")
        back_button.bind(on_press=self.go_home)
        main.add_widget(back_button)

        self.add_widget(main)

    def go_home(self, instance):
        self.manager.current = "home"


class AddPlantScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        main = BoxLayout(orientation="vertical", padding=20, spacing=8)

        main.add_widget(make_label("Add Plant", font_size=28, height=50))

        self.name_input = TextInput(hint_text="Plant name", multiline=False, size_hint_y=None, height=48)
        main.add_widget(self.name_input)

        self.type_spinner = Spinner(
            text="Select Plant Type",
            values=DEFAULT_PLANT_TYPES,
            size_hint_y=None,
            height=48,
            background_normal="",
            background_color=LIGHT_GREEN,
            color=TEXT_DARK
        )
        main.add_widget(self.type_spinner)

        self.location_spinner = Spinner(
            text="Indoor",
            values=("Indoor", "Outdoor"),
            size_hint_y=None,
            height=48,
            background_normal="",
            background_color=LIGHT_GREEN,
            color=TEXT_DARK
        )
        main.add_widget(self.location_spinner)

        self.problem_spinner = Spinner(
            text="No issue",
            values=("No issue", "Yellow leaves or dark spots", "Crispy brown edges", "Reddish freckles", "Soil is always wet", "Pests"),
            size_hint_y=None,
            height=48,
            background_normal="",
            background_color=LIGHT_GREEN,
            color=TEXT_DARK
        )
        main.add_widget(self.problem_spinner)

        self.water_input = TextInput(hint_text="Watering schedule, example: every 7 days", multiline=False, size_hint_y=None, height=48)
        main.add_widget(self.water_input)

        self.light_input = TextInput(hint_text="Light needs, example: bright indirect light", multiline=False, size_hint_y=None, height=48)
        main.add_widget(self.light_input)

        self.notes_input = TextInput(hint_text="Notes", multiline=True, size_hint_y=None, height=80)
        main.add_widget(self.notes_input)

        self.message = make_label("", font_size=16, height=35)
        main.add_widget(self.message)

        save_button = make_button("Save Plant")
        save_button.bind(on_press=self.save_plant)
        main.add_widget(save_button)

        back_button = make_button("Back")
        back_button.bind(on_press=self.go_home)
        main.add_widget(back_button)

        self.add_widget(main)

    def save_plant(self, instance):
        name = self.name_input.text.strip()
        plant_type = self.type_spinner.text

        if name == "":
            self.message.text = "Please enter a plant name."
            return

        if plant_type == "Select Plant Type":
            self.message.text = "Please select a plant type."
            return

        plant = {
            "name": name,
            "type": plant_type,
            "location": self.location_spinner.text,
            "problem": self.problem_spinner.text,
            "watering": self.water_input.text.strip(),
            "light": self.light_input.text.strip(),
            "notes": self.notes_input.text.strip(),
            "last_watered": None
        }

        plants = load_plants()
        plants.append(plant)
        save_plants(plants)

        self.clear_form()
        self.message.text = "Plant saved!"

    def clear_form(self):
        self.name_input.text = ""
        self.type_spinner.text = "Select Plant Type"
        self.location_spinner.text = "Indoor"
        self.problem_spinner.text = "No issue"
        self.water_input.text = ""
        self.light_input.text = ""
        self.notes_input.text = ""

    def go_home(self, instance):
        self.manager.current = "home"


class EditPlantScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.plant_index = None

        main = BoxLayout(orientation="vertical", padding=20, spacing=8)

        main.add_widget(make_label("Edit Plant", font_size=28, height=50))

        self.name_input = TextInput(hint_text="Plant name", multiline=False, size_hint_y=None, height=48)
        main.add_widget(self.name_input)

        self.type_spinner = Spinner(
            text="Select Plant Type",
            values=DEFAULT_PLANT_TYPES,
            size_hint_y=None,
            height=48,
            background_normal="",
            background_color=LIGHT_GREEN,
            color=TEXT_DARK
        )
        main.add_widget(self.type_spinner)

        self.location_spinner = Spinner(
            text="Indoor",
            values=("Indoor", "Outdoor"),
            size_hint_y=None,
            height=48,
            background_normal="",
            background_color=LIGHT_GREEN,
            color=TEXT_DARK
        )
        main.add_widget(self.location_spinner)

        self.problem_spinner = Spinner(
            text="No issue",
            values=("No issue", "Yellow leaves or dark spots", "Crispy brown edges", "Reddish freckles", "Soil is always wet", "Pests"),
            size_hint_y=None,
            height=48,
            background_normal="",
            background_color=LIGHT_GREEN,
            color=TEXT_DARK
        )
        main.add_widget(self.problem_spinner)

        self.water_input = TextInput(hint_text="Watering schedule", multiline=False, size_hint_y=None, height=48)
        main.add_widget(self.water_input)

        self.light_input = TextInput(hint_text="Light needs", multiline=False, size_hint_y=None, height=48)
        main.add_widget(self.light_input)

        self.notes_input = TextInput(hint_text="Notes", multiline=True, size_hint_y=None, height=80)
        main.add_widget(self.notes_input)

        self.message = make_label("", font_size=16, height=35)
        main.add_widget(self.message)

        update_button = make_button("Update Plant")
        update_button.bind(on_press=self.update_plant)
        main.add_widget(update_button)

        delete_button = Button(
            text="Delete Plant",
            size_hint_y=None,
            height=52,
            background_normal="",
            background_color=(0.60, 0.15, 0.15, 1),
            color=WHITE
        )
        delete_button.bind(on_press=self.delete_plant)
        main.add_widget(delete_button)

        back_button = make_button("Back")
        back_button.bind(on_press=self.go_home)
        main.add_widget(back_button)

        self.add_widget(main)

    def load_plant(self, index):
        self.plant_index = index
        plants = load_plants()

        if index < 0 or index >= len(plants):
            self.message.text = "Plant not found."
            return

        plant = plants[index]

        self.name_input.text = plant.get("name", "")
        self.type_spinner.text = plant.get("type", "Other")
        self.location_spinner.text = plant.get("location", "Indoor")
        self.problem_spinner.text = plant.get("problem", "No issue")
        self.water_input.text = plant.get("watering", "")
        self.light_input.text = plant.get("light", "")
        self.notes_input.text = plant.get("notes", "")
        self.message.text = ""

    def update_plant(self, instance):
        if self.plant_index is None:
            self.message.text = "No plant selected."
            return

        name = self.name_input.text.strip()

        if name == "":
            self.message.text = "Please enter a plant name."
            return

        plants = load_plants()

        if self.plant_index < 0 or self.plant_index >= len(plants):
            self.message.text = "Plant not found."
            return

        old_last_watered = plants[self.plant_index].get("last_watered")

        plants[self.plant_index] = {
            "name": name,
            "type": self.type_spinner.text,
            "location": self.location_spinner.text,
            "problem": self.problem_spinner.text,
            "watering": self.water_input.text.strip(),
            "light": self.light_input.text.strip(),
            "notes": self.notes_input.text.strip(),
            "last_watered": old_last_watered
        }

        save_plants(plants)
        self.message.text = "Plant updated!"

    def delete_plant(self, instance):
        if self.plant_index is None:
            self.message.text = "No plant selected."
            return

        plants = load_plants()

        if self.plant_index < 0 or self.plant_index >= len(plants):
            self.message.text = "Plant not found."
            return

        plants.pop(self.plant_index)
        save_plants(plants)
        self.plant_index = None
        self.manager.current = "home"

    def go_home(self, instance):
        self.manager.current = "home"


class CareTipsScreen(Screen):
    def set_plant_index(self, index):
        self.plant_index = index
        plants = load_plants()

        if index < 0 or index >= len(plants):
            self.show_error()
            return

        self.set_plant(plants[index])

    def show_error(self):
        self.clear_widgets()
        main = BoxLayout(orientation="vertical", padding=20, spacing=10)
        main.add_widget(make_label("Plant not found.", font_size=24))
        back_button = make_button("Back to Home")
        back_button.bind(on_press=self.go_home)
        main.add_widget(back_button)
        self.add_widget(main)

    def set_plant(self, plant):
        self.clear_widgets()

        main = BoxLayout(orientation="vertical", padding=20, spacing=8)

        main.add_widget(make_label(plant.get("name", "Unnamed"), font_size=30, height=55))
        main.add_widget(make_label(f"Type: {plant.get('type', 'Other')}", height=35))
        main.add_widget(make_label(f"Last watered: {format_time_since_watered(plant.get('last_watered'))}", height=40))

        main.add_widget(make_label("Care Tip", font_size=24, height=45))

        tip_text = get_care_tip(
            plant.get("type", "Other"),
            plant.get("location", "Indoor"),
            plant.get("problem", "No issue")
        )

        scroll = ScrollView(size_hint=(1, 1))

        tip_label = Label(
            text=tip_text,
            font_size=17,
            color=TEXT_DARK,
            size_hint_y=None,
            halign="left",
            valign="top"
        )
        tip_label.text_size = (Window.width - 60, None)
        tip_label.bind(texture_size=lambda instance, value: setattr(instance, "height", value[1] + 30))

        scroll.add_widget(tip_label)
        main.add_widget(scroll)

        water_button = make_button("Water This Plant")
        water_button.bind(on_press=self.water_current_plant)
        main.add_widget(water_button)

        light_button = make_button("Check Light for This Plant")
        light_button.bind(on_press=self.check_light_for_current_plant)
        main.add_widget(light_button)

        edit_button = make_button("Edit This Plant")
        edit_button.bind(on_press=self.edit_current_plant)
        main.add_widget(edit_button)

        back_button = make_button("Back to Home")
        back_button.bind(on_press=self.go_home)
        main.add_widget(back_button)

        self.add_widget(main)

    def water_current_plant(self, instance):
        plants = load_plants()

        if self.plant_index < 0 or self.plant_index >= len(plants):
            return

        plants[self.plant_index]["last_watered"] = get_now_string()
        save_plants(plants)

        if vibrator is not None:
            try:
                vibrator.vibrate(0.4)
            except Exception:
                pass

        watered_screen = self.manager.get_screen("watered")
        watered_screen.set_message(plants[self.plant_index].get("name", "Plant"))
        self.manager.current = "watered"

    def check_light_for_current_plant(self, instance):
        light_screen = self.manager.get_screen("light")
        light_screen.selected_plant_index = self.plant_index
        self.manager.current = "light"

    def edit_current_plant(self, instance):
        edit_screen = self.manager.get_screen("edit")
        edit_screen.load_plant(self.plant_index)
        self.manager.current = "edit"

    def go_home(self, instance):
        self.manager.current = "home"


class LightSensorScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_plant_index = None
        self.current_lux = None
        self.sensor_enabled = False

    def on_enter(self):
        self.clear_widgets()

        if light is not None:
            try:
                light.enable()
                self.sensor_enabled = True
            except Exception:
                self.sensor_enabled = False

        main = BoxLayout(orientation="vertical", padding=20, spacing=10)

        main.add_widget(make_label("Light Sensor", font_size=30, height=60))

        self.lux_label = make_label("Reading light sensor...", font_size=22, height=70)
        main.add_widget(self.lux_label)

        self.result_label = make_label("Move your phone near the plant's spot.", font_size=18)
        main.add_widget(self.result_label)

        refresh_button = make_button("Refresh Light Reading")
        refresh_button.bind(on_press=self.update_light_reading)
        main.add_widget(refresh_button)

        choose_label = make_label("Choose plant to test:", font_size=18, height=35)
        main.add_widget(choose_label)

        plants = load_plants()
        plant_names = []

        for index, plant in enumerate(plants):
            plant_names.append(f"{index}: {plant.get('name', 'Unnamed')} - {plant.get('type', 'Other')}")

        if len(plant_names) == 0:
            plant_names = ["No saved plants"]

        self.plant_spinner = Spinner(
            text=plant_names[0] if self.selected_plant_index is None else plant_names[self.selected_plant_index],
            values=plant_names,
            size_hint_y=None,
            height=50,
            background_normal="",
            background_color=LIGHT_GREEN,
            color=TEXT_DARK
        )
        main.add_widget(self.plant_spinner)

        test_button = make_button("Test Light for Selected Plant")
        test_button.bind(on_press=self.test_selected_plant)
        main.add_widget(test_button)

        back_button = make_button("Back to Home")
        back_button.bind(on_press=self.go_home)
        main.add_widget(back_button)

        self.add_widget(main)

        Clock.schedule_once(self.update_light_reading, 0.5)

    def update_light_reading(self, *args):
        if light is None:
            self.lux_label.text = "Light sensor not available on this device."
            self.result_label.text = "This usually only works on an Android phone with a light sensor."
            return

        try:
            lux = light.illumination
        except Exception:
            lux = None

        if lux is None:
            self.lux_label.text = "No light reading yet."
            self.result_label.text = "Try again on your Android phone. Some devices do not have an ambient light sensor."
            return

        self.current_lux = float(lux)
        self.lux_label.text = f"Current light: {self.current_lux:.0f} lux"
        self.result_label.text = f"Environment level: {get_light_level_name(self.current_lux)}"

    def test_selected_plant(self, instance):
        plants = load_plants()

        if len(plants) == 0:
            self.result_label.text = "No plants saved yet."
            return

        if self.current_lux is None:
            self.update_light_reading()

        if self.current_lux is None:
            self.result_label.text = "No light reading available yet."
            return

        selected_text = self.plant_spinner.text

        try:
            index_text = selected_text.split(":")[0]
            index = int(index_text)
        except Exception:
            index = 0

        if index < 0 or index >= len(plants):
            self.result_label.text = "Could not find that plant."
            return

        plant = plants[index]
        plant_type = plant.get("type", "Other")

        self.result_label.text = check_light_for_plant(plant_type, self.current_lux)

    def go_home(self, instance):
        self.manager.current = "home"


class PestScreen(Screen):
    def on_enter(self):
        self.clear_widgets()

        main = BoxLayout(orientation="vertical", padding=20, spacing=10)
        main.add_widget(make_label("Common Pest Tips", font_size=28, height=55))

        scroll = ScrollView()
        pest_box = BoxLayout(orientation="vertical", size_hint_y=None, spacing=10)
        pest_box.bind(minimum_height=pest_box.setter("height"))

        for pest, advice in PEST_INFO.items():
            pest_box.add_widget(make_label(f"{pest}\n{advice}", font_size=16, height=120))

        scroll.add_widget(pest_box)
        main.add_widget(scroll)

        back_button = make_button("Back to Home")
        back_button.bind(on_press=self.go_home)
        main.add_widget(back_button)

        self.add_widget(main)

    def go_home(self, instance):
        self.manager.current = "home"


class PlantopediaApp(App):
    def build(self):
        self.title = "Plantopedia"

        sm = ScreenManager()
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(AddPlantScreen(name="add"))
        sm.add_widget(EditPlantScreen(name="edit"))
        sm.add_widget(CareTipsScreen(name="tips"))
        sm.add_widget(PestScreen(name="pests"))
        sm.add_widget(LightSensorScreen(name="light"))
        sm.add_widget(WateredScreen(name="watered"))
        return sm


if __name__ == "__main__":
    PlantopediaApp().run()
