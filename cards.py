from resources import *
from building_layouts import *


class Card:
    def __init__(
        self, name, layout, deck, ability_text, is_feedable=False, is_fed=False, fed_score=0
    ):
        self.name = name
        self.layout = layout
        self.deck = deck
        self.ability_text = ability_text
        self.is_feedable = is_feedable
        self.is_fed = is_fed
        self.fed_score = 0

    def get_layout(self):
        return self.layout

    def get_name(self):
        return self.name

    def get_deck(self):
        """
        Determines the type of the building.
        """
        return self.deck

    def get_card_detail(self):
        if self.is_feedable:
            return f"{self.name}. This card is feedable."
        else:
            return self.name
        
    def score_when_fed(self):
        return self.fed_score


class CottageType(Card):
    def __init_subclass__(cls):
        return super().__init_subclass__()


class FarmType(Card):
    def __init_subclass__(cls):
        return super().__init_subclass__()


class FactoryType(Card):
    def __init_subclass__(cls):
        return super().__init_subclass__()


class TavernType(Card):
    def __init_subclass__(cls):
        return super().__init_subclass__()


class ChapelType(Card):
    def __init_subclass__(cls):
        return super().__init_subclass__()


class TheatreType(Card):
    def __init_subclass__(cls):
        return super().__init_subclass__()


class WellType(Card):
    def __init_subclass__(cls):
        return super().__init_subclass__()


class Monument(Card):
    def __init_subclass__(cls):
        return super().__init_subclass__()


cottage_deck = []
farm_deck = []
factory_deck = []
tavern_deck = []
chapel_deck = []
theatre_deck = []
well_deck = []

cottage = CottageType(
    "Cottage",
    cottage_layout,
    cottage_deck,
    "3VP if this building is fed.",
    is_feedable=True,
    fed_score=3,
)

farm = FarmType(
    "Farm", farm_layout, farm_deck, "Feeds 4 LEAF buildings anywhere in your town."
)
orchard = FarmType(
    "Orchard",
    orchard_layout,
    farm_deck,
    "Feeds all LEAF buildings in the same row and column as FARM.",
)
greenhouse = FarmType(
    "Greenhouse",
    greenhouse_layout,
    farm_deck,
    "Feeds 1 contiguous group of LEAF buildings anywhere in your town.",
)
granary = FarmType(
    "Granary",
    granary_layout,
    farm_deck,
    "Feeds all LEAF buildings in the 8 squares surrounding FARM.",
)

factory = FactoryType(
    "Factory",
    factory_layout,
    factory_deck,
    "When constructed, place 1 of the 5 resources on FACTORY. When another player names this resource, you may place a different resource instead.",
)
warehouse = FactoryType(
    "Warehouse",
    warehouse_layout,
    factory_deck,
    "-1VP for each resource on FACTORY. Each FACTORY can store 3 resources. When another player names a resource, you may place that resource on FACTORY or swap it with another resource on FACTORY.",
)
trading_post = FactoryType(
    "Trading Post",
    trading_post_layout,
    factory_deck,
    "1VP. You may treat FACTORY as a wild resource for future buildings.",
)
bank = FactoryType(
    "Bank",
    bank_layout,
    factory_deck,
    "4VP. When constructed, place a resource on this building that is not on another FACTORY in your town. As Master Builder, you can no longer name the resource on your FACTORY.",
)

tavern = TavernType(
    "Tavern",
    tavern_layout,
    tavern_deck,
    "VP based on your constructed TAVERN. 1: 2VP, 2: 5VP, 3: 9VP, 4: 14VP, 5: 20VP",
)
inn = TavernType(
    "Inn", inn_layout, tavern_deck, "3VP if not in a row or column with another TAVERN."
)
almshouse = TavernType(
    "Almshouse",
    almshouse_layout,
    tavern_deck,
    "VP based on your constructed TAVERN. 1: -1VP, 2: 5VP, 3: -3VP, 4: 15VP, 5: -5VP, 6: 26VP",
)
feast_hall = TavernType(
    "Feast Hall",
    feast_hall_layout,
    tavern_deck,
    "2VP. +1VP if you have more TAVERN than the player on your right.",
)

chapel = ChapelType("Chapel", chapel_layout, chapel_deck, "1VP for each fed COTTAGE.")
temple = ChapelType(
    "Temple", temple_layout, chapel_deck, "4VP if adjacent to 2 or more fed COTTAGE."
)
abbey = ChapelType(
    "Abbey",
    abbey_layout,
    chapel_deck,
    "3VP if not adjacent to FACTORY, TAVERN or THEATRE.",
)
cloister = ChapelType(
    "Cloister",
    cloister_layout,
    chapel_deck,
    "1VP for each CHAPEL in a corner of your town.",
)

theatre = TheatreType(
    "Theatre",
    theatre_layout,
    theatre_deck,
    "1VP for each other unique building type in the same row and column as THEATRE.",
)
bakery = TheatreType(
    "Bakery", bakery_layout, theatre_deck, "3VP if adjacent to FARM or FACTORY."
)
market = TheatreType(
    "Market",
    market_layout,
    theatre_deck,
    "1VP for each THEATRE in the same row or column (not both) as THEATRE.",
)
tailor = TheatreType(
    "Tailor",
    tailor_layout,
    theatre_deck,
    "1VP. +1VP for each THEATRE in the 4 centre squares in your town.",
)

well = WellType("Well", well_layout, well_deck, "1VP for each adjacent COTTAGE.")
fountain = WellType(
    "Fountain", fountain_layout, well_deck, "2VP if adjacent to a WELL."
)
millstone = WellType(
    "Millstone", millstone_layout, well_deck, "2VP if adjacent to a FACTORY or THEATRE."
)
shed = WellType(
    "Shed",
    shed_layout,
    well_deck,
    "1VP. May be constructed on any empty square in your town.",
)

cottage_deck = [cottage]
farm_deck = [farm, orchard, greenhouse, granary]
factory_deck = [factory, warehouse, trading_post, bank]
tavern_deck = [tavern, inn, almshouse, feast_hall]
chapel_deck = [chapel, temple, abbey, cloister]
theatre_deck = [theatre, bakery, market, tailor]
well_deck = [well, fountain, millstone, shed]
monuments_deck = []

all_decks = [
    cottage_deck,
    farm_deck,
    factory_deck,
    tavern_deck,
    chapel_deck,
    theatre_deck,
    well_deck,
]

# MONUMENTS

architects_guild = Monument(
    "Architect's Guild",
    architects_guild_layout,
    monuments_deck,
    "1VP. When Constructed, replace up to 2 buildings in your town with any other building types.",
)
archive_of_the_second_age = Monument(
    "Archive of the Second Age",
    archive_of_the_second_age_layout,
    monuments_deck,
    "1VP for each unique building type (other than MONUMENT) in your town.",
)
barrett_castle = Monument(
    "Barrett Castle",
    barrett_castle_layout,
    monuments_deck,
    "5VP if fed. Counts as 2 COTTAGE.",
    is_feedable=True,
    fed_score=5,
)
cathedral_of_caterina = Monument(
    "Cathedral of Caterina",
    cathedral_of_caterina_layout,
    monuments_deck,
    "2VP. Empty squares in your town are worth 0VP (instead of -1VP).",
)
fort_ironweed = Monument(
    "Fort Ironweed",
    fort_ironweed_layout,
    monuments_deck,
    "7VP. Unless you are the last player in the game, you can no longer take turns as Master Builder.",
)
grand_mausoleum_of_the_rodina = Monument(
    "Grand Mausoleum of the Rodina",
    grand_mausoleum_of_the_rodina_layout,
    monuments_deck,
    "Your unfed COTTAGE are worth 3VP each.",
)
grove_university = Monument(
    "Grove University",
    grove_university_layout,
    monuments_deck,
    "3VP. Immediately place a building on an empty square in your town.",
)
mandras_palace = Monument(
    "Mandras Palace",
    mandras_palace_layout,
    monuments_deck,
    "2VP for each unique adjacent building type.",
)
obelisk_of_the_crescent = Monument(
    "Obelisk of the Crescent",
    obelisk_of_the_crescent_layout,
    monuments_deck,
    "You may place all future buildings on any empty square in your town.",
)
opaleyes_watch = Monument(
    "Opaleye's Watch",
    opaleyes_watch_layout,
    monuments_deck,
    "Immediately place 3 unique buildings on this card. Whenever a player on the left or right of you constructs ",
)
shrine_of_the_elder_tree = Monument(
    "Shrine of the Elder Tree",
    shrine_of_the_elder_tree_layout,
    monuments_deck,
    "VP based on the number of buildings in your town when constructed. 1: 1VP, 2: 2VP, 3: 3VP, 4:4VP, 5: 5VP, 6: 8VP",
)
silva_forum = Monument(
    "Silva Forum",
    silva_forum_layout,
    monuments_deck,
    "1VP. +1VP for each building in your largest contiguous group of buildings of the same type in your town.",
)
the_sky_baths = Monument(
    "The Sky Baths",
    the_sky_baths_layout,
    monuments_deck,
    "2VP for each building type your town is missing.",
)
the_starloom = Monument(
    "The Starloom",
    the_starloom_layout,
    monuments_deck,
    "VP based on when you complete your town. 1st: 6VP, 2nd: 3VP, 3rd: 2VP, 4th+: 0VP",
)
statue_of_the_bondmaker = Monument(
    "Statue of the Bondmaker",
    statue_of_the_bondmaker_layout,
    monuments_deck,
    "When another player names a resource, you may choose to place it on a square with a COTTAGE. Each of your COTTAGE can hold 1 resource.",
)

monuments_deck = [
    architects_guild,
    archive_of_the_second_age,
    barrett_castle,
    cathedral_of_caterina,
    fort_ironweed,
    grand_mausoleum_of_the_rodina,
    grove_university,
    mandras_palace,
    obelisk_of_the_crescent,
    opaleyes_watch,
    shrine_of_the_elder_tree,
    silva_forum,
    the_sky_baths,
    the_starloom,
    statue_of_the_bondmaker,
]

building_input_dict = {
    "cottage": cottage,
    "farm": farm,
    "orchard": orchard,
    "greenhouse": greenhouse,
    "granary": granary,
    "factory": factory,
    "warehouse": warehouse,
    "trading_post": trading_post,
    "bank": bank,
    "tavern": tavern,
    "inn": inn,
    "almshouse": almshouse,
    "feast_hall": feast_hall,
    "chapel": chapel,
    "temple": temple,
    "abbey": abbey,
    "cloister": cloister,
    "theatre": theatre,
    "bakery": bakery,
    "market": market,
    "tailor": tailor,
    "well": well,
    "fountain": fountain,
    "millstone": millstone,
    "shed": shed,
    "architects_guild": architects_guild,
    "archive_of_the_second_age": archive_of_the_second_age,
    "barrett_castle": barrett_castle,
    "cathedral_of_caterina": cathedral_of_caterina,
    "fort_ironweed": fort_ironweed,
    "grand_mausoleum_of_the_rodina": grand_mausoleum_of_the_rodina,
    "grove_university": grove_university,
    "mandras_palace": mandras_palace,
    "obelisk_of_the_crescent": obelisk_of_the_crescent,
    "opaleyes_watch": opaleyes_watch,
    "shrine_of_the_elder_tree": shrine_of_the_elder_tree,
    "silva_forum": silva_forum,
    "the_sky_baths": the_sky_baths,
    "the_starloom": the_starloom,
    "statue_of_the_bondmaker": statue_of_the_bondmaker,
    "wheat": wheat,
    "wood": wood,
    "glass": glass,
    "brick": brick,
    "stone": stone,
    "wild": wild,
}
