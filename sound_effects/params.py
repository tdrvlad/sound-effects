AUDIO_SAMPLES_DIR = '../audio_samples'
AUDIO_SAMPLES_TIMESTAMPS_DIR = '../audio_samples_timestamps'
RECIPES_DIR = '../recipes'
EFFECTS_DIR = '../effects'

AUDIO_FILE = 'output'
TIMESTAMPS_FILE = 'timestamps'

PANEL_LED_PIN = 16
EFFECT_1_PIN = 4
EFFECT_2_PIN = 17
EFFECT_3_PIN = 10
EFFECT_4_PIN = 22
BUTTON_PIN_1 = 23
BUTTON_PIN_2 = 24
BUTTON_PIN_3 = 25
BUTTON_PULL_DOWN = False
RECIPE_LENGTH = 'length'
RECIPE_SAMPLES = 'samples'
RECIPE_SAMPLE_NAME = 'name'
RECIPE_SAMPLE_NAME = 'name'
RECIPE_SAMPLE_FREQUENCY = 'frequency_range'
RECIPE_SAMPLE_FREQUENCY_MIN = 'min'
RECIPE_SAMPLE_FREQUENCY_MAX = 'max'
TIMESTAMPS_START = 'start'
TIMESTAMPS_END = 'stop'

EFFECTS_MAP = {
    "maxim_machine_gun": EFFECT_2_PIN,
    "explosion": EFFECT_1_PIN,
    "falling_bomb": EFFECT_3_PIN,
    "mannlicher_rifle": EFFECT_4_PIN,
    "background": EFFECT_1_PIN
}

BUTTONS_MAP = {
    BUTTON_PIN_1: ("./audio_samples/intro_ro.mp3", "./audio_samples/outro_battle.mp3"),
    BUTTON_PIN_2: ("./audio_samples/intro_en.mp3", "./audio_samples/outro_battle.mp3"),
    BUTTON_PIN_3: ("./audio_samples/intro_doina.mp3", "./audio_samples/outro_battle.mp3"),
}