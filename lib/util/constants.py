from discord_slash import ButtonStyle
from discord_slash.utils.manage_commands import create_option, create_choice
from discord_slash.utils.manage_components import create_button, create_actionrow
from pandas import Series, DataFrame
from pickle import load as pkload

MODE = "DEBUG"

trait_list = {'gender': ['Hen', 'Rooster'],
              'heritage': ['Sultan', 'Dorking', 'Lakenvelder', 'Serama'],
              'talent': ['Jetpack', 'Chickenapult', 'Anvil', 'Dig', 'Blue Egg', 'Cold Snap', 'Moving Walkway',
                         'Fan Group', 'Flight?', 'Growth', 'CK-47', 'Blue Rooster', 'Machete', 'Coober',
                         'Rollerblades',
                         'Teleport', 'Helicopter', 'Devolution', 'Black Hole', 'Royal Procession'],
              'body': ['Istanblue', 'Orange Will', 'Manic Mint', 'English Mustard', "Joker's Jade", 'Purple Wine',
                       'Screamin Green', 'Eggshell', 'Rose', 'Bald Chicken', 'Shocking Pink', 'Sapphire',
                       'Classic',
                       'Wild Moss', 'Merah Red', 'Cherry Dusk', 'Royal Violet', 'Robot', 'Black'],
              'stripes': ['Striped English Mustard', 'Striped Manic Mint', 'Striped Wild moss',
                          'Striped Screamin Green', 'Striped Bald Chicken', 'Striped Istalblue',
                          "Striped Joker's Jade",
                          'Striped Royal Violet', 'Striped Eggshell', 'Striped Shocking Pink'],
              'eye': ['Bulging', 'Bloodshot', 'Shocked', 'Beauty', 'Sleepy', 'Exhausted', 'Determined',
                      'Cockeyed',
                      'Crosseyed', 'Angry', 'Sad', 'Alien', 'Eyepatch', 'Lizard', 'Robot'],
              'beak': ['Vampire', 'Ring'],
              'bg': ['Stone', 'Autumn', 'Summer', 'Winter', 'Flesh', 'Lava', 'Lilac', 'Spring', 'Ocean',
                     'Amethyst'],
              'perfection': ["91", "92", "93", "94", "95", "96", "97", "98", "99", "100"]}

traits = {'Gender': ['Hen', 'Rooster'], 'Animal': ['Chicken'],
          'Heritage': ['Sultan', 'Dorking', 'Lakenvelder', 'Serama'], 'Stock': ['Spicy'],
          'Talent': ['Jetpack', 'Chickenapult', 'Anvil', 'Dig', 'Blue Egg', 'Cold Snap', 'Moving Walkway',
                     'Fan Group', 'Flight?', 'Growth', 'CK-47', 'Blue Rooster', 'Machete', 'Coober', 'Rollerblades',
                     'Teleport', 'Helicopter', 'Devolution', 'Black Hole', 'Royal Procession'],
          'baseBody': ['Istanblue', 'Orange Will', 'Manic Mint', 'English Mustard', "Joker's Jade", 'Purple Wine',
                       'Screamin Green', 'Eggshell', 'Rose', 'Bald Chicken', 'Shocking Pink', 'Sapphire', 'Classic',
                       'Wild Moss', 'Merah Red', 'Cherry Dusk', 'Royal Violet', 'Robot', 'Black'],
          'Stripes': ['Striped English Mustard', 'Striped Manic Mint', 'Striped Wild moss',
                      'Striped Screamin Green', 'Striped Bald Chicken', 'Striped Istalblue', "Striped Joker's Jade",
                      'Striped Royal Violet', 'Striped Eggshell', 'Striped Shocking Pink'],
          'beakColor': ['Yellow', 'Orange', 'Gold', 'White', 'Black'],
          'combColor': ['Green', 'Orange', 'White', 'Black', 'Blue', 'Purple', 'Red', 'Pink', 'Candy', 'Yellow',
                        'Studs', 'Teal'],
          'wattleColor': ['Green', 'Orange', 'White', 'Black', 'Blue', 'Purple', 'Red', 'Pink', 'Candy', 'Yellow',
                          'Teal'],
          'eyesType': ['Bulging', 'Bloodshot', 'Shocked', 'Beauty', 'Sleepy', 'Exhausted', 'Determined', 'Cockeyed',
                       'Crosseyed', 'Angry', 'Sad', 'Alien', 'Eyepatch', 'Lizard', 'Robot'],
          'beakAccessory': ['Vampire', 'Ring'],
          'background': ['Stone', 'Autumn', 'Summer', 'Winter', 'Flesh', 'Lava', 'Lilac', 'Spring', 'Ocean',
                         'Amethyst']}
opensea_link = "https://opensea.io/assets/matic/0x8634666ba15ada4bbc83b9dbf285f73d9e46e4c2/"
warning_message = "**ATTENTION**\nBe advised of scammers wanting to trade you. If you must trade, please message a mod to act as a middleman. Also keep an eye on anyone messaging you asking to trade, make sure their Discord ID's are authentic as there have been cases of impostors. Please stay safe"
filter_index = Series([True for i in range(20100)])
buttons = [create_button(style=ButtonStyle.green, label="Previous", custom_id='prev'),
           create_button(style=ButtonStyle.green, label="Next", custom_id='next')]
actionrow = create_actionrow(*buttons)
cols_to_rename = {'Gender': 'gender', 'Talent': 'talent', 'baseBody': 'body', 'Heritage': 'heritage',
                  'Stripes': 'stripes',
                  'eyesType': 'eye', 'beakAccessory': 'beak', 'background': 'bg'}

percent = {'Alien': 0.91, 'Amethyst': 10, 'Angry': 9, 'Anvil': 7, 'Autumn': 10, 'Bald Chicken': 13, 'Beauty': 9,
           'Black': 10, 'Black Hole': 0.51, 'Bloodshot': 9, 'Blue': 15, 'Blue Egg': 3, 'Blue Rooster': 7, 'Bulging': 9,
           'CK-47': 7, 'Candy': 2, 'Cherry Dusk': 0.54, 'Chicken': 24, 'Chickenapult': 8, 'Classic': 0.83,
           'Cockeyed': 9,
           'Cold Snap': 2, 'Coober': 8, 'Crosseyed': 9, 'Determined': 9, 'Devolution': 2, 'Dig': 4, 'Dorking': 45,
           'Eggshell': 13, 'English Mustard': 13, 'Exhausted': 9, 'Eyepatch': 0.85, 'Fan Group': 4, 'Flesh': 9,
           'Flight?': 7, 'Gold': 31, 'Green': 15, 'Growth': 8, 'Helicopter': 4, 'Hen': 50, 'Istanblue': 5, 'Jetpack': 4,
           "Joker's Jade": 10, 'Lakenvelder': 33, 'Lava': 10, 'Lilac': 10, 'Lizard': 0.88, 'Machete': 7,
           'Manic Mint': 10, 'Merah Red': 2, 'Moving Walkway': 2, 'Ocean': 9, 'Orange': "", 'Orange Will': 4,
           'Pink': 10,
           'Purple': 2, 'Purple Wine': 5, 'Red': 15, 'Ring': 0.77, 'Robot': '', 'Rollerblades': 8, 'Rooster': 50,
           'Rose': 2, 'Royal Procession': 0.55, 'Royal Violet': 2, 'Sad': 9, 'Sapphire': 5, 'Screamin Green': 10,
           'Serama': 6, 'Shocked': 9, 'Shocking Pink': 2, 'Sleepy': 9, 'Spicy': 100, 'Spring': 9, 'Stone': 10,
           'Striped Bald Chicken': '', 'Striped Eggshell': '', 'Striped English Mustard': '', 'Striped Istalblue': '',
           "Striped Joker's Jade": '', 'Striped Manic Mint': '', 'Striped Royal Violet': '',
           'Striped Screamin Green': '', 'Striped Shocking Pink': '', 'Striped Wild moss': '', 'Studs': '',
           'Sultan': 16,
           'Summer': 10, 'Teal': 0.27, 'Teleport': 7, 'Vampire': 0.86, 'White': "", 'Wild Moss': 3, 'Winter': 10,
           'Yellow': 31}
choices_egg = (
    'Not Dropped Yet', ':face_with_monocle: You think you are smarter than me. huh!',
    ':point_up: Its right there buddy',
    'Oops ! Got an egg instead')
choices_tip = (
    "You can get info of all chickens of somenone by typing.\n!owner <ADDRESS> ",
    "You can also use !t instead of !token.",
    "You can also use !o instead of !owner.",
    "We are always available to help you so clear your doubts in #questions channel.",
    "You can also use slash commands try now type \n/token",
    "The most valuable information can be found in pinned messages.",
    "Our first drop of 14000 chickens was sold within 9 minutes.",
    "While buying chickens from drop you dont have to pay gas fees . We take care of that.",
    "You can also click on Chicken name to go to its opensea page",
    "bg in the /filter command stands for background",
    "In later on updates you can see Opensea listed price in the result."
    "Use !verify command to verify your account. It give you access to a lot of perks in the future."
)
if MODE == "DEBUG":
    guild_ids = [632799582350475265]
    warn_channel_ids = [854215344075440138]
    main_guild = 632799582350475265
    cluck_norris = 874318078836613182
    attila = 874318165339930724
    chicking = 874318221950476389
    coop = 874318291194241048
    rancher = 875015372833689630
    main_ch = 854215344075440138
else:
    warn_channel_ids = [868331067894013992, 866666604092063754, 854418136890474576, 854418163122307142]
    guild_ids = [846537412058021888, 868330968321257472]
    cluck_norris = 860211150994145301
    attila = 860211281918296064
    chicking = 860210698196746300
    coop = 860211204818862110
    rancher = 874297498271887461
    main_ch = 874679638364946582
PREFIX = "!"

cache_data = {}
lc_cache = {}
owner = {}

options_find = [
    create_option(
        name=category,
        description="Choose one of the options",
        option_type=3,
        required=False,
        choices=[
            create_choice(name=trait, value=trait) for trait in trait_list[category]])
    for category in trait_list.keys()]

to_be_handled = []
options_token = [
    create_option(
        name="tokenid",
        description="ID of the Token",
        option_type=4,
        required=True)]

df: DataFrame = pkload(open("df", "rb"))
df.rename(columns=cols_to_rename, inplace=True)
