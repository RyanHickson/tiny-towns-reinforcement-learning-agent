from buildingLayouts import *
from cardDecks import *

class Card:
    def __init__(self, name, layout, deck, abilityText, isFeedable=False):
        self.name = name
        self.layout = layout
        self.deck = deck
        self.abilityText = abilityText
        self.isFeedable = isFeedable

    def getLayout(self):
        return self.layout
    
    def getName(self):
        return self.name
    
    def getCardDetail(self):
        if self.isFeedable:
            return f"{self.name}. This card is feedable."
        else:
            return self.name


cottage = Card("Cottage", cottageLayout, cottageDeck, "3VP if this building is fed.", isFeedable=True)

farm = Card("Farm", farmLayout, farmDeck, "Feeds 4 LEAF buildings anywhere in your town.")
orchard = Card("Orchard", orchardLayout, farmDeck, "Feeds all LEAF buildings in the same row and column as FARM.")
greenhouse = Card("Greenhouse", greenhouseLayout, farmDeck, "Feeds 1 contiguous group of LEAF buildings anywhere in your town.")
granary = Card("Granary", granaryLayout, farmDeck, "Feeds all LEAF buildings in the 8 squares surrounding FARM.")

factory = Card("Factory", factoryLayout, factoryDeck, "When constructed, place 1 of the 5 resources on FACTORY. When another player names this resource, you may place a different resource instead.")
warehouse = Card("Warehouse", warehouseLayout, factoryDeck, "-1VP for each resource on FACTORY. Each FACTORY can store 3 resources. When another player names a resource, you may place that resource on FACTORY or swap it with another resource on FACTORY.")
tradingPost = Card("Trading Post", tradingPostLayout, factoryDeck, "1VP. You may treat FACTORY as a wild resource for future buildings.")
bank = Card("Bank", bankLayout, factoryDeck, "4VP. When constructed, place a resource on this building that is not on another FACTORY in your town. As Master Builder, you can no longer name the resource on your FACTORY.")

tavern = Card("Tavern", tavernLayout, tavernDeck, "VP based on your constructed TAVERN. 1: 2VP, 2: 5VP, 3: 9VP, 4: 14VP, 5: 20VP")
inn = Card("Inn", innLayout, tavernDeck, "3VP if not in a row or column with another TAVERN.")
almshouse = Card("Almshouse", almshouseLayout, tavernDeck, "VP based on your constructed TAVERN. 1: -1VP, 2: 5VP, 3: -3VP, 4: 15VP, 5: -5VP, 6: 26VP")
feastHall = Card("Feast Hall", feastHallLayout, tavernDeck, "2VP. +1VP if you have more TAVERN than the player on your right.")

chapel = Card("Chapel", chapelLayout, chapelDeck, "1VP for each fed COTTAGE.")
temple = Card("Temple", templeLayout, chapelDeck, "4VP if adjacent to 2 or more fed COTTAGE.")
abbey = Card("Abbey", abbeyLayout, chapelDeck, "3VP if not adjacent to FACTORY, TAVERN or THEATRE.")
cloister = Card("Cloister", cloisterLayout, chapelDeck, "1VP for each CHAPEL in a corner of your town.")

theatre = Card("Theatre", theatreLayout, theatreDeck, "1VP for each other unique building type in the same row and column as THEATRE.")
bakery = Card("Bakery", bakeryLayout, theatreDeck, "3VP if adjacent to FARM or FACTORY.")
market = Card("Market", marketLayout, theatreDeck, "1VP for each THEATRE in the same row or column (not both) as THEATRE.")
tailor = Card("Tailor", tailorLayout, theatreDeck, "1VP. +1VP for each THEATRE in the 4 centre squares in your town.")

well = Card("Well", wellLayout, wellDeck, "1VP for each adjacent COTTAGE.")
fountain = Card("Fountain", fountainLayout, wellDeck, "2VP if adjacent to a WELL.")
millstone = Card("Millstone", millstoneLayout, wellDeck, "2VP if adjacent to a FACTORY or THEATRE.")
shed = Card("Shed", shedLayout, wellDeck, "1VP. May be constructed on any empty square in your town.")

cottageDeck = [cottage]

farmDeck = [farm, orchard, greenhouse, granary]

factoryDeck = [factory, warehouse, tradingPost, bank]

tavernDeck = [tavern, inn, almshouse, feastHall]

chapelDeck = [chapel, temple, abbey, cloister]

theatreDeck = [theatre, bakery, market, tailor]

wellDeck = [well, fountain, millstone, shed]

allDecks = [cottageDeck,
            farmDeck,
            factoryDeck,
            tavernDeck,
            chapelDeck,
            theatreDeck,
            wellDeck]

# MONUMENTS

architectsGuild = Card("Architect's Guild", architectsGuildLayout, monumentsDeck, "1VP. When Constructed, replace up to 2 buildings in your town with any other building types.")
archiveOfTheSecondAge = Card("Archive of the Second Age", archiveOfTheSecondAgeLayout, monumentsDeck, "1VP for each unique building type (other than MONUMENT) in your town.")
barettCastle = Card("Barrett Castle", barrettCastleLayout, monumentsDeck, "5VP if fed. Counts as 2 COTTAGE.", isFeedable=True)
cathedralOfCaterina = Card("Cathedral of Caterina", cathedralOfCaterinaLayout, monumentsDeck, "2VP. Empty squares in your town are worth 0VP (instead of -1VP).")
fortIronweed = Card("Fort Ironweed", fortIronweedLayout, monumentsDeck, "7VP. Unless you are the last player in the game, you can no longer take turns as Master Builder.")
grandMausoleumOfTheRodina = Card("Grand Mausoleum of the Rodina", grandMausoleumOfTheRodinaLayout, monumentsDeck, "Your unfed COTTAGE are worth 3VP each.")
groveUniversity = Card("Grove University", groveUniversityLayout, monumentsDeck, "3VP. Immediately place a building on an empty square in your town.")
mandrasPalace = Card("Mandras Palace", mandrasPalaceLayout, monumentsDeck, "2VP for each unique adjacent building type.")
obeliskOfTheCrescent = Card("Obelisk of the Crescent", obeliskOfTheCrescentLayout, monumentsDeck, "You may place all future buildings on any empty square in your town.")
opaleyesWatch = Card("Opaleye's Watch", opaleyesWatchLayout, monumentsDeck, "Immediately place 3 unique buildings on this card. Whenever a player on the left or right of you constructs ")
shrineOfTheElderTree = Card("Shrine of the Elder Tree", shrineOfTheElderTreeLayout, monumentsDeck, "VP based on the number of buildings in your town when constructed. 1: 1VP, 2: 2VP, 3: 3VP, 4:4VP, 5: 5VP, 6: 8VP")
silvaForum = Card("Silva Forum", silvaForumLayout, monumentsDeck, "1VP. +1VP for each building in your largest contiguous group of buildings of the same type in your town.")
theSkyBaths = Card("The Sky Baths", theSkyBathsLayout, monumentsDeck, "2VP for each building type your town is missing.")
theStarloom = Card("The Starloom", theStarloomLayout, monumentsDeck, "VP based on when you complete your town. 1st: 6VP, 2nd: 3VP, 3rd: 2VP, 4th+: 0VP")
statueOfTheBondmaker = Card("Statue of the Bondmaker", statueOfTheBondmakerLayout, monumentsDeck, "When another player names a resource, you may choose to place it on a square with a COTTAGE. Each of your COTTAGE can hold 1 resource.")

monumentsDeck = [architectsGuild,
                archiveOfTheSecondAge,
                barettCastle,
                cathedralOfCaterina,
                fortIronweed,
                grandMausoleumOfTheRodina,
                groveUniversity,
                mandrasPalace,
                obeliskOfTheCrescent,
                opaleyesWatch,
                shrineOfTheElderTree,
                silvaForum,
                theSkyBaths,
                theStarloom,
                statueOfTheBondmaker]