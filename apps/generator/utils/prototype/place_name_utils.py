"""
Place name utilities for formatting and abbreviating location data.

Provides functions to parse, abbreviate, and format place names
for better display in family tree charts.
"""

import re
from typing import Optional


# Mapping of full country names to abbreviations
COUNTRY_ABBREVIATIONS = {
    "united states of america": "USA",
    "united states": "USA",
    "us": "USA",
    "u.s.": "USA",
    "u.s.a.": "USA",
    "united kingdom": "UK",
    "great britain": "GB",
}

# UK and Irish county abbreviations
UK_COUNTY_ABBREVIATIONS = {
    # English counties
    "bedfordshire": "Beds.",
    "berkshire": "Berks.",
    "buckinghamshire": "Bucks.",
    "cambridgeshire": "Cambs.",
    "cheshire": "Ches.",
    "cornwall": "Cornwall",
    "cumberland": "Cumb.",
    "derbyshire": "Derbs.",
    "devon": "Devon",
    "dorset": "Dors.",
    "durham": "Dur.",
    "essex": "Essex",
    "gloucestershire": "Glos.",
    "hampshire": "Hants.",
    "herefordshire": "Heref.",
    "hertfordshire": "Herts.",
    "huntingdonshire": "Hunts.",
    "kent": "Kent",
    "lancashire": "Lancs.",
    "leicestershire": "Leics.",
    "lincolnshire": "Lincs.",
    "london": "Lon.",
    "middlesex": "Middx",
    "norfolk": "Norf.",
    "northamptonshire": "Northants.",
    "northumberland": "Northumb.",
    "nottinghamshire": "Notts.",
    "oxfordshire": "Oxon.",
    "rutland": "Rut.",
    "shropshire": "Salop.",
    "somerset": "Som.",
    "staffordshire": "Staffs.",
    "suffolk": "Suff.",
    "surrey": "Surr.",
    "sussex": "Suss.",
    "warwickshire": "Warks.",
    "westmorland": "Westm.",
    "wiltshire": "Wilts.",
    "worcestershire": "Worcs.",
    "yorkshire": "Yorks.",
    # Welsh counties
    "anglesey": "Angl.",
    "breconshire": "Brecs.",
    "caernarfonshire": "Caerns.",
    "cardiganshire": "Cards.",
    "carmarthenshire": "Carms.",
    "denbighshire": "Denbs.",
    "flintshire": "Flints.",
    "glamorgan": "Glam.",
    "merionethshire": "Merion.",
    "monmouthshire": "Mons.",
    "montgomeryshire": "Montg.",
    "pembrokeshire": "Pembs.",
    "radnorshire": "Rads.",
    # Scottish counties
    "aberdeenshire": "Aber.",
    "angus": "Angus",
    "argyllshire": "Argyll",
    "ayrshire": "Ayr",
    "banffshire": "Banff",
    "berwickshire": "Berwick",
    "buteshire": "Bute",
    "caithness": "Caith.",
    "clackmannanshire": "Clackm.",
    "cromarty": "Crom.",
    "dumfriesshire": "Dumfries",
    "dunbartonshire": "Dunbar",
    "east lothian": "E. Loth.",
    "edinburgh": "Edin.",
    "elginshire": "Elgin",
    "fife": "Fife",
    "forfarshhire": "Forfar",
    "haddingtonshire": "Hadd.",
    "inverness-shire": "Inver.",
    "linlithgowshire": "Linlith.",
    "kincardineshire": "Kincar.",
    "kinross-shire": "Kinross",
    "kirkcudbrightshire": "Kirkcud.",
    "lanarkshire": "Lanark",
    "midlothian": "Midloth.",
    "moray": "Moray",
    "nairn": "Nairn",
    "orkney": "Orkney",
    "peeblesshire": "Peebles",
    "perthshire": "Perth",
    "renfrewshire": "Renfrew",
    "ross-shire": "Ross",
    "ross and cromarty": "Ross and Crom.",
    "roxburghshire": "Roxb.",
    "selkirkshire": "Selk.",
    "stirlingshire": "Stirl.",
    "sutherland": "Suther.",
    "west lothian": "W. Loth.",
    "wigtownshire": "Wigtown",
    "zetland": "Zetland",
    "shetland": "Zetland",
    # Irish counties
    "antrim": "Antrim",
    "armagh": "Armagh",
    "carlow": "Carlow",
    "cavan": "Cavan",
    "clare": "Clare",
    "cork": "Cork",
    "donegal": "Donegal",
    "down": "Down",
    "dublin": "Dublin",
    "fermanagh": "Ferm.",
    "galway": "Galway",
    "kerry": "Kerry",
    "kildare": "Kildare",
    "kilkenny": "Kilk.",
    "laois": "Laois",
    "leitrim": "Leitrim",
    "limerick": "Lim.",
    "londonderry": "Derry",
    "longford": "Long.",
    "louth": "Louth",
    "mayo": "Mayo",
    "meath": "Meath",
    "monaghan": "Monag.",
    "offaly": "Offaly",
    "roscommon": "Rosc.",
    "sligo": "Sligo",
    "tipperary": "Tipp.",
    "tyrone": "Tyrone",
    "waterford": "Waterf.",
    "westmeath": "Westmeath",
    "wexford": "Wexford",
    "wicklow": "Wicklow",
}

# Country name to flag emoji mapping
COUNTRY_FLAGS = {
    "usa": "🇺🇸",
    "us": "🇺🇸",
    "united states": "🇺🇸",
    "united states of america": "🇺🇸",
    "u.s.": "🇺🇸",
    "u.s.a.": "🇺🇸",
    "uk": "🇬🇧",
    "u.k.": "🇬🇧",
    "united kingdom": "🇬🇧",
    "great britain": "🇬🇧",
    "gb": "🇬🇧",
    "england": "🏴󠁧󠁢󠁥󠁮󠁧󠁿",
    "scotland": "🏴󠁧󠁢󠁳󠁣󠁴󠁿",
    "wales": "🏴󠁧󠁢󠁷󠁬󠁳󠁿",
    "n. ireland": "🇺🇸",
    "northern ireland": "🇺🇸",
    "canada": "🇨🇦",
    "australia": "🇦🇺",
    "germany": "🇩🇪",
    "deutschland": "🇩🇪",
    "preussen": "🇩🇪",
    "preußen": "🇩🇪",
    "prussia": "🇩🇪",
    "france": "🇫🇷",
    "italy": "🇮🇹",
    "spain": "🇪🇸",
    "mexico": "🇲🇽",
    "ireland": "🇮🇪",
    "netherlands": "🇳🇱",
    "belgium": "🇧🇪",
    "switzerland": "🇨🇭",
    "austria": "🇦🇹",
    "poland": "🇵🇱",
    "sweden": "🇸🇪",
    "sverige": "🇸🇪",
    "norway": "🇳🇴",
    "denmark": "🇩🇰",
    "finland": "🇫🇮",
    "portugal": "🇵🇹",
    "brazil": "🇧🇷",
    "argentina": "🇦🇷",
    "japan": "🇯🇵",
    "china": "🇨🇳",
    "india": "🇮🇳",
    "russia": "🇷🇺",
    "south africa": "🇿🇦",
    "new zealand": "🇳🇿",
}

# Country name to ISO 3166-1 alpha-2 country code mapping
COUNTRY_CODES = {
    "usa": "us",
    "us": "us",
    "united states": "us",
    "united states of america": "us",
    "u.s.": "us",
    "u.s.a.": "us",
    "uk": "gb",
    "united kingdom": "gb",
    "great britain": "gb",
    "gb": "gb",
    "england": "gb-eng",
    "scotland": "gb-sct",
    "wales": "gb-wls",
    "northern ireland": "gb-nir",
    "canada": "ca",
    "australia": "au",
    "germany": "de",
    "deutschland": "de",
    "preussen": "de",
    "preußen": "de",
    "prussia": "de",
    "france": "fr",
    "italy": "it",
    "spain": "es",
    "mexico": "mx",
    "ireland": "ie",
    "netherlands": "nl",
    "belgium": "be",
    "switzerland": "ch",
    "austria": "at",
    "poland": "pl",
    "sweden": "se",
    "sverige": "se",
    "norway": "no",
    "denmark": "dk",
    "finland": "fi",
    "portugal": "pt",
    "brazil": "br",
    "argentina": "ar",
    "japan": "jp",
    "china": "cn",
    "india": "in",
    "russia": "ru",
    "south africa": "za",
    "new zealand": "nz",
}

# Mapping of full US state names to abbreviations
US_STATE_ABBREVIATIONS = {
    "alabama": "AL",
    "alaska": "AK",
    "arizona": "AZ",
    "arkansas": "AR",
    "california": "CA",
    "colorado": "CO",
    "connecticut": "CT",
    "delaware": "DE",
    "florida": "FL",
    "georgia": "GA",
    "hawaii": "HI",
    "idaho": "ID",
    "illinois": "IL",
    "indiana": "IN",
    "iowa": "IA",
    "kansas": "KS",
    "kentucky": "KY",
    "louisiana": "LA",
    "maine": "ME",
    "maryland": "MD",
    "massachusetts": "MA",
    "michigan": "MI",
    "minnesota": "MN",
    "mississippi": "MS",
    "missouri": "MO",
    "montana": "MT",
    "nebraska": "NE",
    "nevada": "NV",
    "new hampshire": "NH",
    "new jersey": "NJ",
    "new mexico": "NM",
    "new york": "NY",
    "north carolina": "NC",
    "north dakota": "ND",
    "ohio": "OH",
    "oklahoma": "OK",
    "oregon": "OR",
    "pennsylvania": "PA",
    "rhode island": "RI",
    "south carolina": "SC",
    "south dakota": "SD",
    "tennessee": "TN",
    "texas": "TX",
    "utah": "UT",
    "vermont": "VT",
    "virginia": "VA",
    "washington": "WA",
    "west virginia": "WV",
    "wisconsin": "WI",
    "wyoming": "WY",
    "district of columbia": "DC",
}

# Canadian province abbreviations
CANADA_PROVINCE_ABBREVIATIONS = {
    "alberta": "AB",
    "british columbia": "BC",
    "manitoba": "MB",
    "new brunswick": "NB",
    "newfoundland": "NL",
    "nova scotia": "NS",
    "ontario": "ON",
    "prince edward island": "PE",
    "quebec": "QC",
    "saskatchewan": "SK",
}

# Swedish county (län) abbreviations - Länsbokstäver
# Official vehicle registration codes used until 1973, still used for genealogical abbreviations
SWEDISH_COUNTY_CODES = {
    "stockholm": "AB",
    "stockholms län": "AB",
    "uppsala": "C",
    "uppsala län": "C",
    "södermanland": "D",
    "södermanlands län": "D",
    "östergötland": "E",
    "östergötlands län": "E",
    "jönköping": "F",
    "jönköpings län": "F",
    "kronoberg": "G",
    "kronobergs län": "G",
    "kalmar": "H",
    "kalmar län": "H",
    "blekinge": "K",
    "blekinge län": "K",
    "skåne": "M",
    "skåne län": "M",
    "halland": "N",
    "hallands län": "N",
    "västra götaland": "O",
    "västra götalands län": "O",
    "gävleborg": "X",
    "gävleborgs län": "X",
    "västernorrland": "Y",
    "västernorrlands län": "Y",
    "jämtland": "Z",
    "jämtlands län": "Z",
    "västerbotten": "AC",
    "västerbottens län": "AC",
    "norrbotten": "BD",
    "norrbottens län": "BD",
    "gotland": "I",
    "gotlands län": "I",
    "värmland": "S",
    "värmlands län": "S",
    "örebro": "T",
    "örebro län": "T",
    "västmanland": "U",
    "västmanlands län": "U",
    "dalarna": "W",
    "dalarnas län": "W",
}

# French department codes (departements) - INSEE codes
# Two-digit codes used for postal codes and administrative filing
FRENCH_DEPARTMENT_CODES = {
    "ain": "01",
    "aisne": "02",
    "allier": "03",
    "alpes-de-haute-provence": "04",
    "hautes-alpes": "05",
    "alpes-maritimes": "06",
    "ardèche": "07",
    "ardennes": "08",
    "ariège": "09",
    "aube": "10",
    "aude": "11",
    "aveyron": "12",
    "bouches-du-Rhône": "13",
    "calvados": "14",
    "cantal": "15",
    "charente": "16",
    "charente-maritime": "17",
    "cher": "18",
    "corrèze": "19",
    "corse": "20",
    "corse-du-sud": "2A",
    "haute-corse": "2B",
    "côte-d'Or": "21",
    "côtes-d'Armor": "22",
    "creuse": "23",
    "dordogne": "24",
    "doubs": "25",
    "drôme": "26",
    "eure": "27",
    "eure-et-loir": "28",
    "finistère": "29",
    "gard": "30",
    "haute-garonne": "31",
    "gers": "32",
    "gironde": "33",
    "hérault": "34",
    "ille-et-vilaine": "35",
    "indre": "36",
    "indre-et-loire": "37",
    "isère": "38",
    "jura": "39",
    "landes": "40",
    "loir-et-cher": "41",
    "loire": "42",
    "haute-loire": "43",
    "loire-atlantique": "44",
    "loiret": "45",
    "lot": "46",
    "lot-et-garonne": "47",
    "lozère": "48",
    "maine-et-loire": "49",
    "manche": "50",
    "marne": "51",
    "haute-marne": "52",
    "mayenne": "53",
    "meurthe-et-moselle": "54",
    "meuse": "55",
    "morbihan": "56",
    "moselle": "57",
    "nièvre": "58",
    "nord": "59",
    "oise": "60",
    "orne": "61",
    "pas-de-calais": "62",
    "puy-de-dôme": "63",
    "pyrénées-atlantiques": "64",
    "hautes-pyrenees": "65",
    "pyrénées-orientales": "66",
    "bas-rhin": "67",
    "haut-rhin": "68",
    "rhône": "69",
    "haute-saône": "70",
    "saône-et-loire": "71",
    "sarthe": "72",
    "savoie": "73",
    "haute-savoie": "74",
    "paris": "75",
    "seine-maritime": "76",
    "seine-et-marne": "77",
    "yvelines": "78",
    "deux-sèvres": "79",
    "somme": "80",
    "tarn": "81",
    "tarn-et-garonne": "82",
    "var": "83",
    "vaucluse": "84",
    "vendée": "85",
    "vienne": "86",
    "haute-vienne": "87",
    "vosges": "88",
    "yonne": "89",
    "territoire de belfort": "90",
    "essonne": "91",
    "hauts-de-seine": "92",
    "seine-saint-denis": "93",
    "val-de-marne": "94",
    "val-d'oise": "95",
    # Corsica variants
    "corse": "20",
    # Historical departments
    "loire-inférieure": "44",
    "seine-inférieure": "76",
}

# Combine all state/province abbreviations (full name -> abbreviation)
STATE_ABBREVIATIONS = {
    **US_STATE_ABBREVIATIONS,
    **CANADA_PROVINCE_ABBREVIATIONS,
}

# Create reverse lookup: abbreviation -> abbreviation (for parsing already-abbreviated places)
# e.g., "il" -> "IL", "ca" -> "CA"
STATE_ABBREVIATIONS_REVERSE = {v.lower(): v for v in STATE_ABBREVIATIONS.values()}
# Merge into main dict for lookup
STATE_ABBREVIATIONS = {**STATE_ABBREVIATIONS, **STATE_ABBREVIATIONS_REVERSE}

# Set of all US state names (lowercase) for quick lookup
US_STATES = {s.lower() for s in US_STATE_ABBREVIATIONS.keys()}

# Common place name part abbreviations
# These are applied to street suffixes and geographical terms
PLACE_PART_ABBREVIATIONS = {
    # Mountains and terrain
    "mountain": "Mtn",
    "mtn": "Mtn",
    "mount": "Mt",
    "mt": "Mt",
    "mountains": "Mtns",
    # Saints and religious
    "saint": "St",
    "sainte": "Ste",
    "st": "St",
    "ste": "Ste",
    # Streets and roads
    "avenue": "Ave",
    "ave": "Ave",
    "street": "St",
    "boulevard": "Blvd",
    "blvd": "Blvd",
    "road": "Rd",
    "rd": "Rd",
    "lane": "Ln",
    "ln": "Ln",
    "drive": "Dr",
    "dr": "Dr",
    "court": "Ct",
    "ct": "Ct",
    "place": "Pl",
    "pl": "Pl",
    "terrace": "Ter",
    "ter": "Ter",
    "circle": "Cir",
    "cir": "Cir",
    "parkway": "Pkwy",
    "pkwy": "Pkwy",
    "highway": "Hwy",
    "hwy": "Hwy",
    "freeway": "Fwy",
    "fwy": "Fwy",
    "expressway": "Expy",
    "expy": "Expy",
    "trail": "Trl",
    "trl": "Trl",
    "way": "Wy",
    "wy": "Wy",
    "alley": "Aly",
    "aly": "Aly",
    # Water and geography
    "river": "Riv",
    "riv": "riv",
    "island": "Is",
    "is": "Is",
    "lake": "Lk",
    "lk": "Lk",
    "sea": "Sea",
    "ocean": "Ocean",
    "bay": "Bay",
    "harbor": "Harbor",
    "port": "Port",
    "creek": "Crk",
    "crk": "Crk",
    "stream": "Strm",
    "brook": "Brk",
    "brk": "Brk",
    # Fortifications and settlements
    "fort": "Ft",
    "ft": "Ft",
    "heights": "Hts",
    "hts": "Hts",
    "junction": "Jct",
    "jct": "Jct",
    "center": "Ctr",
    "ctr": "Ctr",
    "centre": "Ctr",
    "station": "Sta",
    "sta": "Sta",
    "springs": "Spgs",
    "spgs": "Spgs",
    "spring": "Spg",
    "spg": "Spg",
    "falls": "Fls",
    "fls": "Fls",
    " gorge": "Gorge",
    "valley": "Vly",
    "vly": "Vly",
    "hollow": "Hlw",
    "hlw": "Hlw",
    "prairie": "Pr",
    "plains": "Plns",
    "plns": "Plns",
    "meadow": "Mdw",
    "mdw": "Mdw",
    "hill": "Hl",
    "hl": "Hl",
    "hills": "Hls",
    "hls": "Hls",
}

# Known country identifiers (includes English names + multilingual variants for parsing)
KNOWN_COUNTRIES = {
    # English canonical names
    "usa",
    "us",
    "u.s.",
    "u.s.a.",
    "united states",
    "united states of america",
    "uk",
    "u.k.",
    "gb",
    "great britain",
    "united kingdom",
    "canada",
    "australia",
    "germany",
    "deutschland",
    "preussen",
    "preußen",
    "prussia",
    "france",
    "italy",
    "spain",
    "mexico",
    "ireland",
    "scotland",
    "wales",
    "england",
    "n. ireland",
    "northern ireland",
    "netherlands",
    "belgium",
    "switzerland",
    "austria",
    "poland",
    "portugal",
    "brazil",
    "argentina",
    "japan",
    "china",
    "india",
    "russia",
    "south africa",
    "new zealand",
    "sweden",
    "sverige",
    "norway",
    "norge",
    "denmark",
    "danmark",
    "finland",
    "suède",
    "norge",
    "danemark",
    "finlande",
    "france",
    "francia",
    "frankrijk",
    "frankreich",
    "francía",
    # German variants
    "niedersachsen",
    "bayern",
    "schleswig-holstein",
    "brandenburg",
    # French variants
    "allemagne",
    "espagne",
    "pologne",
    "suisse",
    "belgique",
    "hollande",
    "pays-bas",
    "suède",
    "norvège",
    "danemark",
    "finlande",
    # Spanish variants
    "alemania",
    "españa",
    "méxico",
    "méjico",
    "italia",
    "polonia",
    "suiza",
    "bélgica",
    "austria",
    "suecia",
    "noruega",
    "dinamarca",
    "finlandia",
    "brasil",
    # Italian variants
    "germania",
    "messico",
    "svizzera",
    "belgio",
    "austria",
    "svezia",
    "norvegia",
    "danimarca",
    "finlandia",
    "portogallo",
    "brasile",
    # Dutch variants
    "duitsland",
    "nederland",
    "zwitserland",
    "belgië",
    "oostenrijk",
    "zweden",
    "noorwegen",
    "denemarken",
    # Polish variants
    "niemcy",
    "włochy",
    "hiszpania",
    "szwajcaria",
    "holandia",
    "szwecja",
    "norwegia",
    "dania",
    # Russian variants
    "германия",
    "франция",
    "италия",
    "испания",
    "польша",
    "швейцария",
    "бельгия",
    "нидерланды",
    "австрия",
    "швеция",
    "норвегия",
    "дания",
    "финляндия",
    "португалия",
    "бразилия",
    "аргентина",
    # Portuguese variants
    "alemanha",
    "itália",
    "espanha",
    "polônia",
    "suíça",
    "países baixos",
    "suécia",
    "dinamarca",
    "finlândia",
    # Hungarian variants
    "magyarország",
    "németország",
    "franciaország",
    "olaszország",
    "spanyolország",
    "lengyelország",
    "svájc",
    "ausztria",
    "svédország",
    "norvégia",
    "dánia",
    "finnország",
    # Historical
    "west germany",
    "east germany",
    "yugoslavia",
    "czechoslovakia",
    "soviet union",
    "ussr",
}

# Multilingual country name variants -> ISO 3166-1 alpha-2 code
# This maps foreign language names to standardized codes for flag lookup
# Covers common genealogical variants (European focus + major immigrant origins)
COUNTRY_NAME_VARIANTS = {
    # German
    "deutschland": "de",
    "niedersachsen": "de",
    "bayern": "de",
    "schleswig-holstein": "de",
    "brandenburg": "de",
    # French
    "allemagne": "de",
    "france": "fr",
    "espagne": "es",
    "italie": "it",
    "pologne": "pl",
    "suisse": "ch",
    "belgique": "be",
    "hollande": "nl",  # Netherlands
    "pays-bas": "nl",
    "autriche": "at",
    "suède": "se",
    "norvège": "no",
    "danemark": "dk",
    "finlande": "fi",
    "portugal": "pt",
    "brésil": "br",
    "argentine": "ar",
    # Spanish
    "alemania": "de",
    "españa": "es",
    "méxico": "mx",
    "méjico": "mx",
    "italia": "it",
    "polonia": "pl",
    "suiza": "ch",
    "bélgica": "be",
    "austria": "at",
    "suecia": "se",
    "noruega": "no",
    "dinamarca": "dk",
    "finlandia": "fi",
    "brasil": "br",
    "argentina": "ar",
    # Italian
    "germania": "de",
    "spagna": "es",
    "messico": "mx",
    "polonia": "pl",
    "svizzera": "ch",
    "belgio": "be",
    "austria": "at",
    "svezia": "se",
    "norvegia": "no",
    "danimarca": "dk",
    "finlandia": "fi",
    "portogallo": "pt",
    "brasile": "br",
    "argentina": "ar",
    # Dutch
    "duitsland": "de",
    "nederland": "nl",
    "zwitserland": "ch",
    "belgië": "be",
    "oostenrijk": "at",
    "zweden": "se",
    "noorwegen": "no",
    "denemarken": "dk",
    "finland": "fi",
    # Polish
    "niemcy": "de",
    "francja": "fr",
    "włochy": "it",
    "hiszpania": "es",
    "polska": "pl",
    "szwajcaria": "ch",
    "belgia": "be",
    "holandia": "nl",
    "austria": "at",
    "szwecja": "se",
    "norwegia": "no",
    "dania": "dk",
    "finlandia": "fi",
    "portugalia": "pt",
    "brazylia": "br",
    "argentyna": "ar",
    # Russian / Cyrillic
    "германия": "de",
    "франция": "fr",
    "италия": "it",
    "испания": "es",
    "польша": "pl",
    "швейцария": "ch",
    "бельгия": "be",
    "нидерланды": "nl",
    "австрия": "at",
    "швеция": "se",
    "норвегия": "no",
    "дания": "dk",
    "финляндия": "fi",
    "португалия": "pt",
    "бразилия": "br",
    "аргентина": "ar",
    # Portuguese
    "alemanha": "de",
    "itália": "it",
    "espanha": "es",
    "polônia": "pl",
    "suíça": "ch",
    "bélgica": "be",
    "países baixos": "nl",
    "áustria": "at",
    "suécia": "se",
    "noruega": "no",
    "dinamarca": "dk",
    "finlândia": "fi",
    "brasil": "br",
    "argentina": "ar",
    # Hungarian
    "magyarország": "hu",
    "nemetorszag": "de",  # ASCII approximation
    "németország": "de",
    "franciaorszag": "fr",
    "franciaország": "fr",
    "olaszorszag": "it",
    "olaszország": "it",
    "spanyolorszag": "es",
    "spanyolország": "es",
    "lengyelorszag": "pl",
    "lengyelország": "pl",
    "svajc": "ch",
    "svájc": "ch",
    "belgium": "be",
    "hollandia": "nl",
    "ausztria": "at",
    "svédorszag": "se",
    "svédország": "se",
    "norvégia": "no",
    "dánia": "dk",
    "finnorszag": "fi",
    "finnország": "fi",
    "portugália": "pt",
    "brazília": "br",
    "argentína": "ar",
    # Romanian
    "germania": "fr",
    "franţa": "fr",
    "italia": "it",
    "spania": "es",
    "polonia": "pl",
    "elveţia": "ch",
    "belgia": "be",
    "olanda": "nl",
    "austria": "at",
    "suedia": "se",
    "norvegia": "no",
    "finlanda": "fi",
    # Czech / Slovak
    "německo": "de",
    "francIE": "fr",
    "italsko": "it",
    "španělsko": "es",
    "polsko": "pl",
    "švýcarsko": "ch",
    "belgie": "be",
    "nizozemsko": "nl",
    "rakousko": "at",
    "švédsko": "se",
    "norsko": "no",
    "dánsko": "dk",
    "finsko": "fi",
    # Greek
    "γερμανία": "de",
    "γαλλία": "fr",
    "ιταλία": "it",
    "ισπανία": "es",
    "πολωνία": "pl",
    "ελβετία": "ch",
    "βέλγιο": "be",
    "ολλανδία": "nl",
    "αυστρία": "at",
    "σουηδία": "se",
    "νορβηγία": "no",
    "δανία": "dk",
    "φινλανδία": "fi",
    # Turkish
    "almanya": "de",
    "fransa": "fr",
    "ispanya": "es",
    "italya": "it",
    "polonya": "pl",
    "isviçre": "ch",
    "belçika": "be",
    "hollanda": "nl",
    "avusturya": "at",
    "isveç": "se",
    "norveç": "no",
    "danimarka": "dk",
    "finlandiya": "fi",
    # Scandinavian (other)
    "tyskland": "de",  # Swedish
    "tyskland": "de",  # Norwegian
    "tyskland": "de",  # Danish
    "norge": "no",  # Norwegian
    # Historical / Deprecated
    "prussia": "de",
    "preussen": "de",
    "preußen": "de",
    "west germany": "de",
    "east germany": "de",
    "yugoslavia": "rs",  # Now Serbia mostly
    "czechoslovakia": "cz",
    "soviet union": "ru",
    "ussr": "ru",
}

# UK constituent countries (for flag purposes)
UK_COUNTRIES = {"england", "scotland", "wales", "n. ireland", "northern ireland"}


def detect_country(place: str) -> dict:
    """
    Detect the country of a place name.

    In most cases, the final field is the country. For UK places, if "UK" appears
    but there's England/Scotland/Wales/Northern Ireland before it, use that as
    the "country" for flag purposes.

    Args:
        place: Comma-separated place name

    Returns:
        Dictionary with keys:
            - country: The detected country name (or UK constituent for UK places)
            - is_us: True if place is in the US
            - is_uk: True if place is in the UK
            - is_sweden: True if place is in Sweden
            - is_france: True if place is in France
            - raw_country: The raw last part if it's a country identifier
    """
    if not place:
        return {
            "country": "",
            "is_us": False,
            "is_uk": False,
            "is_sweden": False,
            "is_france": False,
            "raw_country": "",
        }

    parts = [p.strip() for p in place.split(",")]
    if not parts:
        return {
            "country": "",
            "is_us": False,
            "is_uk": False,
            "is_sweden": False,
            "is_france": False,
            "raw_country": "",
        }

    last_part = parts[-1].lower().strip()
    raw_country = parts[-1] if last_part in KNOWN_COUNTRIES else ""

    is_us = False
    is_uk = False
    is_sweden = False
    is_france = False
    country = raw_country

    # Check if it's a US place
    if last_part in {
        "usa",
        "us",
        "u.s.",
        "u.s.a.",
        "united states",
        "united states of america",
    }:
        is_us = True
    elif last_part in US_STATES:
        is_us = True

    # Check if it's a UK place
    if last_part in {"uk", "u.k.", "gb", "great britain", "united kingdom"}:
        is_uk = True
        # Check if there's a UK constituent country before UK
        if len(parts) >= 2:
            second_last = parts[-2].lower().strip()
            if second_last in UK_COUNTRIES:
                country = parts[-2]  # Use England/Scotland/Wales/N. Ireland
            else:
                # UK without constituent - use the raw country (UK)
                country = parts[-1]
    elif last_part in UK_COUNTRIES:
        is_uk = True
        country = parts[-1]

    # Check if it's Sweden
    if last_part in {"sweden", "sverige"}:
        is_sweden = True

    # Check if it's France
    if last_part in {"france", "francia", "frankrijk", "frankreich", "francía"}:
        is_france = True

    return {
        "country": country,
        "is_us": is_us,
        "is_uk": is_uk,
        "is_sweden": is_sweden,
        "is_france": is_france,
        "raw_country": raw_country,
    }


def parse_place(place: str) -> dict:
    """
    Parse a comma-separated place name into components.

    For American places: town, county, state, country (4 parts) or town, county, state (3 parts)
    The parts before the state are treated as town + county.

    Returns:
        Dictionary with keys: city, county, township, state, country, parts_count, is_us, is_uk
    """
    if not place:
        return {
            "city": "",
            "county": "",
            "township": "",
            "state": "",
            "country": "",
            "other": "",
            "parts_count": 0,
            "is_us": False,
            "is_uk": False,
            "is_sweden": False,
            "is_france": False,
        }

    # Detect country first
    country_info = detect_country(place)

    parts = [p.strip() for p in place.split(",")]
    parts_count = len(parts)

    result = {
        "city": "",
        "county": "",
        "township": "",
        "state": "",
        "country": "",
        "other": "",
        "parts_count": parts_count,
        "is_us": country_info["is_us"],
        "is_uk": country_info["is_uk"],
        "is_sweden": country_info["is_sweden"],
        "is_france": country_info["is_france"],
    }

    if parts_count == 0:
        return result

    def is_explicit_county(part: str) -> bool:
        part_lower = part.lower()
        # Check for various county markers
        return (
            "county" in part_lower
            or "co." in part_lower
            or part_lower.endswith(", co")
            or part_lower.endswith(" co")
        )

    def is_explicit_township(part: str) -> bool:
        part_lower = part.lower()
        # Check for various township markers - be lenient since GEDCOM varies
        # Includes: township, twp, twp., ward (treated similarly)
        return (
            "township" in part_lower
            or part_lower.endswith(" twp")
            or part_lower.endswith(" twp.")
            or ", twp" in part_lower
            or "ward" in part_lower
        )

    # Use global KNOWN_COUNTRIES for country detection
    known_countries = KNOWN_COUNTRIES

    # Find country
    last_lower = parts[-1].lower().strip()
    has_country = last_lower in known_countries

    if has_country:
        result["country"] = parts[-1]
        parts = parts[:-1]
        parts_count = len(parts)

    # Find state
    if parts_count >= 1:
        last_lower = parts[-1].lower().strip()
        if last_lower in STATE_ABBREVIATIONS:
            result["state"] = parts[-1]
            parts = parts[:-1]
            parts_count = len(parts)

    # Detect Swedish counties (län) and French departments
    # Check remaining parts for Swedish/French county/department patterns
    # Swedish: usually "Town, County, Country" (e.g., "Säby, Jönköping, Sweden")
    # French: usually "Town, Department, Region, Country" (e.g., "Appeville, Eure, Haute-Normandie, France")
    # OR "Town, Department, Country" (e.g., "Marseille, Bouches-du-Rhône, France")

    # Helper for case-insensitive French department lookup
    def find_french_department(part: str) -> str | None:
        part_lower = part.lower().strip()
        if part_lower in FRENCH_DEPARTMENT_CODES:
            return part
        # Also try with title-case handling for hyphenated names like Bouches-du-Rhône
        part_title = part.strip()
        if part_title in FRENCH_DEPARTMENT_CODES:
            return part_title
        # Try with first letter capitalized (handles most French department names)
        part_cap = part_title.capitalize()
        if part_cap in FRENCH_DEPARTMENT_CODES:
            return part_cap
        # Try case-insensitive search for complex names
        for key in FRENCH_DEPARTMENT_CODES:
            if key.lower() == part_lower:
                return key
        return None

    if parts_count >= 1:
        # For Swedish: check last part for "län" or known county
        last_lower = parts[-1].lower().strip()
        if "län" in last_lower or last_lower in SWEDISH_COUNTY_CODES:
            result["state"] = parts[-1]
            parts = parts[:-1]
            parts_count = len(parts)
        # For French: check all parts for department (typically the 2nd to last before region)
        # Common patterns: "Town, Department, Region, Country" or "Town, Department, Country"
        elif parts_count >= 2:
            # Check second-to-last part (could be department)
            dept = find_french_department(parts[-2])
            if dept:
                result["state"] = dept
                # Also mark the region as "other" to be filtered out
                if parts_count >= 3:
                    result["other"] = parts[-1]
                parts = parts[:-2] if parts_count >= 3 else parts[:-1]
                parts_count = len(parts)
            # If no department found in second-to-last, check last part
            else:
                dept = find_french_department(parts[-1])
                if dept:
                    result["state"] = dept
                    parts = parts[:-1]
                    parts_count = len(parts)

    # Now we have remaining parts - these are town/county
    # For American style: first part is town, second is county (if 2 parts after removing state/country)
    if parts_count >= 2:
        # Check for explicit township first
        if is_explicit_township(parts[-1]):
            result["township"] = parts[-1]
            parts = parts[:-1]
            parts_count = len(parts)

        # Check for explicit county marker
        # Don't treat UK constituent countries as counties
        uk_countries_lower = {
            "england",
            "scotland",
            "wales",
            "n. ireland",
            "northern ireland",
        }
        if is_explicit_county(parts[-1]):
            result["county"] = parts[-1]
            parts = parts[:-1]
        elif parts_count >= 2 and parts[-1].lower().strip() not in uk_countries_lower:
            # US pattern with 2 parts remaining: town, county
            # The SECOND part (parts[-1]) is the county, FIRST is town
            # This applies to: town, county, state (3 parts) or town, county, state, country (4 parts)
            # Don't treat UK countries as counties
            result["county"] = parts[-1]
            parts = parts[:-1]

        # What remains is city/town
        if len(parts) >= 1:
            result["city"] = ", ".join(parts) if len(parts) > 1 else parts[0]
    elif parts_count == 1:
        # Single part remaining - could be city or county
        # Don't treat UK constituent countries as counties
        uk_countries_lower = {
            "england",
            "scotland",
            "wales",
            "n. ireland",
            "northern ireland",
        }
        if (
            is_explicit_county(parts[0])
            and parts[0].lower().strip() not in uk_countries_lower
        ):
            result["county"] = parts[0]
        elif is_explicit_township(parts[0]):
            result["township"] = parts[0]
        else:
            result["city"] = parts[0]

    return result


def abbreviate_country(country: str) -> str:
    """
    Abbreviate country name if known.

    Args:
        country: Full country name

    Returns:
        Abbreviated country name or original if not recognized
    """
    if not country:
        return country

    country_lower = country.lower().strip()
    return COUNTRY_ABBREVIATIONS.get(country_lower, country)


def abbreviate_state(state: str) -> str:
    """
    Abbreviate state/province name if known.

    Args:
        state: Full state or province name

    Returns:
        Abbreviated state name or original if not recognized
    """
    if not state:
        return state

    state_lower = state.lower().strip()
    return STATE_ABBREVIATIONS.get(state_lower, state)


def abbreviate_swedish_county(county: str) -> str:
    """
    Abbreviate Swedish county (län) name to its code.

    Args:
        county: Full county name (e.g., "Jönköpings län", "Jönköping")

    Returns:
        Abbreviated county code (e.g., "F") or original if not recognized
    """
    if not county:
        return county

    county_lower = county.lower().strip()
    # Try direct match first
    if county_lower in SWEDISH_COUNTY_CODES:
        return SWEDISH_COUNTY_CODES[county_lower]

    # Try without " län" suffix
    if county_lower.endswith(" län"):
        county_without_lan = county_lower[:-4]
        if county_without_lan in SWEDISH_COUNTY_CODES:
            return SWEDISH_COUNTY_CODES[county_without_lan]

    return county


def abbreviate_french_department(department: str) -> str:
    """
    Abbreviate French department name to its INSEE code.

    Args:
        department: Full department name (e.g., "Calvados", "Eure")

    Returns:
        Abbreviated department code (e.g., "14", "27") or original if not recognized
    """
    if not department:
        return department

    department_lower = department.lower().strip()
    # Try exact match first
    if department_lower in FRENCH_DEPARTMENT_CODES:
        return FRENCH_DEPARTMENT_CODES[department_lower]
    # Try case-insensitive search
    for key, value in FRENCH_DEPARTMENT_CODES.items():
        if key.lower() == department_lower:
            return value
    return department


def abbreviate_place_name_parts(place: str) -> str:
    """
    Abbreviate common place name parts (street suffixes, geographical terms).

    Args:
        place: Place string to abbreviate

    Returns:
        Place string with common parts abbreviated
    """
    if not place:
        return place

    # Split by comma and process each part
    parts = place.split(",")
    abbreviated_parts = []

    for part in parts:
        part_stripped = part.strip()
        part_lower = part_stripped.lower()

        # Check for exact matches at word boundaries
        # First check for full word matches (surrounded by spaces or at start/end)
        for full_word, abbrev in PLACE_PART_ABBREVIATIONS.items():
            # Use word boundary matching
            import re

            # Match whole word only (case-insensitive)
            pattern = r"\b" + re.escape(full_word) + r"\b"
            if re.search(pattern, part_lower):
                # Replace with proper case abbreviation
                part_stripped = re.sub(
                    pattern, lambda m: abbrev, part_stripped, flags=re.IGNORECASE
                )
                break  # Only apply first match to avoid double-replacement

        abbreviated_parts.append(part_stripped)

    return ", ".join(abbreviated_parts)


def format_place(
    place: str,
    use_country_abbrev: bool = False,
    use_state_abbrev: bool = False,
    hide_us_counties: bool = True,
    show_township: bool = True,
    show_country: bool = True,
    hide_usa_with_state: bool = True,
    country_first: bool = False,
    auto_shorten: bool = False,
    abbreviate_uk_counties: bool = False,
    abbreviate_sweden_counties: bool = False,
    abbreviate_france_departments: bool = False,
    abbreviate_place_parts: bool = False,
) -> str:
    """
    Format a place name based on settings.

    Args:
        place: Original place string (comma-separated)
        use_country_abbrev: Abbreviate country name (USA, UK, etc.)
        use_state_abbrev: Abbreviate state/province to 2-letter code
        hide_us_counties: Hide US county names when part of Town,County,State pattern
        show_township: Include township in output (only if detected as township)
        show_country: Include country in output
        hide_usa_with_state: Hide "USA" when a US state is present
        country_first: Put country before other parts
        auto_shorten: When show_country is False and result would have 3+ parts,
                      reduce to last 2 parts (removes first part). Useful for
                      places like "Town, Region, County, Country" → "Region, County"
        abbreviate_uk_counties: Abbreviate UK/Ireland county names (e.g., Yorkshire → Yorks.)
        abbreviate_sweden_counties: Abbreviate Swedish counties to codes (e.g., Jönköpings län → F)
        abbreviate_france_departments: Abbreviate French departments to codes (e.g., Calvados → 14)
        abbreviate_place_parts: Abbreviate common place parts (e.g., Street → St, Mountain → Mtn)

    Returns:
        Formatted place string
    """
    if not place:
        return place

    # Apply place part abbreviations first (before other processing)
    if abbreviate_place_parts:
        place = abbreviate_place_name_parts(place)

    parsed = parse_place(place)

    # Check hide_usa_with_state BEFORE abbreviating (need original state name)
    should_show_country = show_country
    if hide_usa_with_state and show_country:
        country_lower = parsed["country"].lower() if parsed["country"] else ""
        if country_lower in [
            "usa",
            "us",
            "u.s.",
            "u.s.a.",
            "united states",
            "united states of america",
        ]:
            if parsed["state"]:
                state_lower = parsed["state"].lower().strip()
                if state_lower in STATE_ABBREVIATIONS:
                    should_show_country = False

    # Apply abbreviations
    if use_country_abbrev and parsed["country"]:
        parsed["country"] = abbreviate_country(parsed["country"])

    if use_state_abbrev and parsed["state"]:
        parsed["state"] = abbreviate_state(parsed["state"])

    # Apply Swedish county abbreviations
    if abbreviate_sweden_counties and parsed["state"] and parsed["is_sweden"]:
        parsed["state"] = abbreviate_swedish_county(parsed["state"])
        # Hide Sweden when county code is shown
        if parsed["country"] and parsed["country"].lower() in {"sweden", "sverige"}:
            parsed["country"] = ""

    # Apply French department abbreviations
    if abbreviate_france_departments and parsed["state"] and parsed["is_france"]:
        parsed["state"] = abbreviate_french_department(parsed["state"])
        # Hide France when department code is shown
        if parsed["country"] and parsed["country"].lower() in {
            "france",
            "francia",
            "frankrijk",
            "frankreich",
            "francía",
        }:
            parsed["country"] = ""

    # Determine if we should hide the county
    # Only hide US counties when: is US place AND has both city and county
    should_hide_county = (
        hide_us_counties and parsed["is_us"] and parsed["county"] and parsed["city"]
    )

    # Filter out county/township parts based on settings (handles unusual GEDCOM formats)
    # This catches cases where county/township aren't properly parsed into their fields
    original_parts = [p.strip() for p in place.split(",")]
    filtered_parts = []

    for part in original_parts:
        part_lower = part.lower()
        is_county = (
            "county" in part_lower
            or part_lower.endswith(", co")
            or part_lower.endswith(" co")
            or part_lower.endswith(" co.")
        )
        is_township = (
            "township" in part_lower or "twp" in part_lower or "ward" in part_lower
        )

        # Include part unless it's a county/township we're hiding
        if is_county and should_hide_county:
            continue
        if is_township and not show_township:
            continue
        filtered_parts.append(part)

    # Rebuild parsed from filtered parts (for "other" field)
    # Then rebuild output parts based on settings
    parts = []

    # Rebuild parsed from filtered parts (for "other" field)
    # Then rebuild output parts based on settings
    parts = []

    # Clean up county suffix for display (only if showing - i.e., not hiding)
    # Country-specific formatting:
    # - US: append "Co." after county name (e.g., "Marion County" → "Marion Co.")
    # - Ireland: prepend "Co." before county name (e.g., "County Cork" → "Co. Cork")
    # - UK/France/others: show as-is (no Co. modification)
    display_county = ""
    if not should_hide_county and parsed["county"]:
        county = parsed["county"]
        county_lower = county.lower()

        # Check if it's Ireland (place ends in Ireland, or has Irish county pattern)
        is_ireland = (
            parsed["country"].lower() == "ireland" if parsed["country"] else False
        )
        is_us = parsed["is_us"]

        if is_ireland:
            # Irish counties: "County Cork" → "Co. Cork", "Co. Cork" stays "Co. Cork"
            if county_lower.startswith("county "):
                display_county = "Co. " + county[7:].strip()
            elif county_lower.startswith("county,"):
                display_county = "Co." + county[6:].strip()
            elif "co." in county_lower or "co " in county_lower:
                display_county = county  # Already has Co.
            else:
                display_county = "Co. " + county
        elif is_us:
            # US counties: "Marion County" → "Marion Co."
            if county_lower.endswith(" county"):
                display_county = county[:-7].strip() + " Co."
            elif county_lower.endswith(", county"):
                display_county = county[:-9].strip() + " Co."
            elif "co." in county_lower or " co " in county_lower:
                display_county = county  # Already has Co.
            else:
                display_county = county + " Co."
        else:
            # UK, France, others: show as-is without Co. modification
            display_county = county

    # Clean up township suffix for display (only if showing)
    display_township = ""
    if show_township and parsed["township"]:
        township = parsed["township"]
        township_lower = township.lower()
        if township_lower.endswith(" township"):
            display_township = township[:-9].strip()
        elif township_lower.endswith(", township"):
            display_township = township[:-11].strip()
        elif township_lower.endswith(" twp"):
            display_township = township[:-4].strip()
        elif township_lower.endswith(" twp."):
            display_township = township[:-5].strip()
        else:
            display_township = township

    # Always order: town, county, state, country (for US places) or town, state, country (for non-US)
    # County goes after state so it can be hidden
    if not should_hide_county:
        # Order: town, township, county, state, country
        if country_first and should_show_country and parsed["country"]:
            parts.append(parsed["country"])

        if parsed["city"]:
            parts.append(parsed["city"])

        if show_township and display_township:
            parts.append(display_township)

        # County goes after state (for US: town, county, state, USA)
        if display_county:
            parts.append(display_county)

        if parsed["state"]:
            parts.append(parsed["state"])

        if not country_first and should_show_country and parsed["country"]:
            parts.append(parsed["country"])
    else:
        # Order when county hidden: town, township, state, country
        if country_first and should_show_country and parsed["country"]:
            parts.append(parsed["country"])

        if parsed["city"]:
            parts.append(parsed["city"])

        if show_township and display_township:
            parts.append(display_township)

        if parsed["state"]:
            parts.append(parsed["state"])

        if not country_first and should_show_country and parsed["country"]:
            parts.append(parsed["country"])

    if parsed["other"]:
        parts.append(parsed["other"])

    # Filter out "other" (regions) when French/Swedish abbreviations are enabled
    # French regions (e.g., Haute-Normandie, Basse-Normandie) should be hidden
    # when the department code is shown
    if (abbreviate_france_departments and parsed.get("is_france")) or (
        abbreviate_sweden_counties and parsed.get("is_sweden")
    ):
        # Remove the "other" part (region) from the output
        filtered_parts = [p for p in parts if p != parsed.get("other", "")]
        result = ", ".join(filtered_parts)
    else:
        result = ", ".join(parts)

    # Auto-shorten: when enabled and result has 3+ parts,
    # reduce to first 2 parts (removes middle parts and country)
    # Works with or without country shown
    # E.g.: US: "Town, County, State, Country" → "Town, State"
    #       UK: "Town, County, Region, Country" → "Town, Country"
    #       France: "Town, Department, Region, Country" → "Town, Department"
    if auto_shorten:
        result_parts = [p.strip() for p in result.split(",")]

        # Detect country from parsed info
        is_france = (
            parsed.get("country", "").lower() == "france"
            if parsed.get("country")
            else False
        )

        # UK identifiers for filtering
        uk_identifiers = {
            "uk",
            "u.k.",
            "gb",
            "great britain",
            "united kingdom",
            "england",
            "scotland",
            "wales",
            "n. ireland",
            "northern ireland",
        }

        if not show_country:
            # Remove UK-related identifiers entirely
            result_parts = [
                p for p in result_parts if p.lower().strip() not in uk_identifiers
            ]
        else:
            # When showing country, prefer constituent country over UK
            has_constituent = any(
                p.lower().strip()
                in {"england", "scotland", "wales", "n. ireland", "northern ireland"}
                for p in result_parts
            )
            if has_constituent:
                result_parts = [
                    p
                    for p in result_parts
                    if p.lower().strip()
                    not in {"uk", "u.k.", "gb", "great britain", "united kingdom"}
                ]

        # Now shorten to first 2 parts
        if len(result_parts) >= 3:
            # For France (when show_country=False): keep first 2 parts (town, department)
            # For others or when show_country=True: keep first and last (town, region/state)
            if is_france and not show_country:
                result = result_parts[0] + ", " + result_parts[1]
            else:
                result = result_parts[0] + ", " + result_parts[-1]
        elif len(result_parts) >= 1:
            result = ", ".join(result_parts)

    # Abbreviate UK/Ireland county names if enabled
    if abbreviate_uk_counties:
        result_parts = [p.strip() for p in result.split(",")]
        abbreviated_parts = []
        for part in result_parts:
            part_lower = part.lower()
            if part_lower in UK_COUNTY_ABBREVIATIONS:
                abbreviated_parts.append(UK_COUNTY_ABBREVIATIONS[part_lower])
            else:
                abbreviated_parts.append(part)
        result = ", ".join(abbreviated_parts)

    return result


def get_place_short(
    place: str,
    max_parts: int = 2,
) -> str:
    """
    Get a shortened version of place name.

    Args:
        place: Original place string
        max_parts: Maximum number of parts to include (from the end)

    Returns:
        Shortened place string (e.g., "Illinois, USA")
    """
    if not place:
        return place

    parts = [p.strip() for p in place.split(",")]
    if len(parts) <= max_parts:
        return place

    # Take the last max_parts
    return ", ".join(parts[-max_parts:])


def format_place_from_settings(place: str, settings: dict, flag: str = "") -> str:
    """
    Format a place name using settings from the generator.

    Args:
        place: Original place string
        settings: Dictionary with settings like:
            - place_use_country_abbrev: bool
            - place_use_state_abbrev: bool
            - place_hide_us_counties: bool (formerly place_show_county inverted)
            - place_show_township: bool
            - place_show_country: bool
            - place_hide_usa_with_state: bool
            - place_country_first: bool
            - place_auto_shorten: bool
            - place_abbreviate_uk_counties: bool
            - place_abbreviate_sweden_counties: bool
            - place_abbreviate_france_departments: bool
            - place_abbreviate_place_parts: bool
        flag: Optional flag emoji to append to place

    Returns:
        Formatted place string
    """
    if not place:
        return place

    formatted = format_place(
        place,
        use_country_abbrev=settings.get("place_use_country_abbrev", False),
        use_state_abbrev=settings.get("place_use_state_abbrev", False),
        hide_us_counties=settings.get("place_hide_us_counties", True),
        show_township=settings.get("place_show_township", True),
        show_country=settings.get("place_show_country", True),
        hide_usa_with_state=settings.get("place_hide_usa_with_state", True),
        country_first=settings.get("place_country_first", False),
        auto_shorten=settings.get("place_auto_shorten", False),
        abbreviate_uk_counties=settings.get("place_abbreviate_uk_counties", False),
        abbreviate_sweden_counties=settings.get(
            "place_abbreviate_sweden_counties", False
        ),
        abbreviate_france_departments=settings.get(
            "place_abbreviate_france_departments", False
        ),
        abbreviate_place_parts=settings.get("place_abbreviate_place_parts", False),
    )

    if flag:
        formatted = f"{formatted} {flag}"

    return formatted


def get_flag_from_place(place: str) -> str:
    """
    Extract country flag emoji from a place string.

    Args:
        place: Place string (e.g., "Chicago, Illinois, USA")

    Returns:
        Flag emoji if country detected, empty string otherwise
    """
    if not place:
        return ""

    parsed = parse_place(place)
    country = parsed.get("country", "")

    if not country:
        return ""

    country_lower = country.lower().strip()

    # Try direct lookup first, then fall back to variant mapping
    if country_lower in COUNTRY_FLAGS:
        return COUNTRY_FLAGS[country_lower]

    # Check multilingual variants
    variant_code = COUNTRY_NAME_VARIANTS.get(country_lower)
    if variant_code and variant_code in COUNTRY_FLAGS:
        return COUNTRY_FLAGS[variant_code]

    return ""


def _get_country_code(country_name: str) -> str:
    """
    Normalize a country name to ISO 3166-1 alpha-2 code.

    Args:
        country_name: Country name in any language

    Returns:
        ISO 2-letter code (e.g., 'de', 'fr') or empty string if not found
    """
    if not country_name:
        return ""

    country_lower = country_name.lower().strip()

    # First check: direct match in COUNTRY_CODES
    if country_lower in COUNTRY_CODES:
        return COUNTRY_CODES[country_lower]

    # Second check: multilingual variant mapping
    variant_code = COUNTRY_NAME_VARIANTS.get(country_lower)
    if variant_code:
        return variant_code

    return ""


def get_flag_image_path(place: str) -> str:
    """
    Get the flag image path for a place string.

    Args:
        place: Place string (e.g., "Chicago, Illinois, USA")

    Returns:
        Relative path to flag image (e.g., "charts/images/flags/us.png") if country detected, empty string otherwise
    """
    if not place:
        return ""

    parsed = parse_place(place)
    country = parsed.get("country", "")

    if not country:
        return ""

    # Use helper to normalize country name to ISO code (supports multilingual variants)
    country_code = _get_country_code(country)

    if not country_code:
        return ""

    return f"charts/images/flags/{country_code}.png"


# Date constants for UK and Ireland flag logic
UK_FOUNDING_DATE = "1801-01-01"  # United Kingdom of Great Britain and Ireland formed
IRELAND_INDEPENDENCE_DATE = "1922-12-06"  # Irish Free State established


def get_flag_from_place_with_settings(
    place: str,
    birth_date: str = None,
    death_date: str = None,
    show_uk_flag: bool = False,
    show_ireland_flag: bool = False,
) -> str:
    """
    Get flag emoji for a place, respecting UK/Ireland flag date settings.

    For UK places:
    - Default: Show constituent country flag (England, Scotland, Wales)
    - If show_uk_flag=True: Show UK Union Jack, but only if birth/death is after 1801-01-01

    For Ireland places:
    - Default: Show Ireland flag
    - If show_ireland_flag=False: Show Ireland flag (default behavior)
    - If show_ireland_flag=True: Still shows Ireland flag, but only if date is between 1801-01-01 and 1922-12-06
      (when Ireland was part of the UK)

    Args:
        place: Place string
        birth_date: Birth date in format YYYY-MM-DD (optional)
        death_date: Death date in format YYYY-MM-DD (optional)
        show_uk_flag: If True, show UK flag instead of constituent country flag
        show_ireland_flag: If True, apply date restrictions for Ireland flag

    Returns:
        Flag emoji
    """
    if not place:
        return ""

    parsed = parse_place(place)
    country = parsed.get("country", "")

    if not country:
        return ""

    country_lower = country.lower().strip()

    # Helper to parse date
    def parse_date(date_str):
        if not date_str:
            return None
        try:
            from datetime import datetime

            return datetime.strptime(date_str[:10], "%Y-%m-%d")
        except (ValueError, TypeError):
            return None

    def is_date_after(target_date_str, check_date):
        if not check_date:
            return False
        target = parse_date(target_date_str)
        check = parse_date(check_date)
        if not target or not check:
            return False
        return check >= target

    def is_date_between(start_date_str, end_date_str, check_date):
        if not check_date:
            return False
        start = parse_date(start_date_str)
        end = parse_date(end_date_str)
        check = parse_date(check_date)
        if not start or not end or not check:
            return False
        return start <= check <= end

    # Handle UK places
    if parsed.get("is_uk"):
        # Default: show constituent country flag (England, Scotland, Wales, N. Ireland)
        if not show_uk_flag:
            return COUNTRY_FLAGS.get(country_lower, "")

        # If show_uk_flag is enabled, only show UK flag if date is after 1801
        # Check both birth and death dates - if either is after 1801, show UK flag
        if is_date_after(UK_FOUNDING_DATE, birth_date) or is_date_after(
            UK_FOUNDING_DATE, death_date
        ):
            return COUNTRY_FLAGS.get("uk", "🇬🇧")

        # Otherwise return empty (no flag)
        return ""

    # Handle Ireland places
    if country_lower == "ireland":
        if not show_ireland_flag:
            # Default: always show Ireland flag
            return COUNTRY_FLAGS.get("ireland", "🇮🇪")

        # If show_ireland_flag is enabled, only show Ireland flag if date is between 1801 and 1922
        # (when Ireland was part of the UK)
        date_in_range = is_date_between(
            UK_FOUNDING_DATE, IRELAND_INDEPENDENCE_DATE, birth_date
        ) or is_date_between(UK_FOUNDING_DATE, IRELAND_INDEPENDENCE_DATE, death_date)
        if date_in_range:
            return COUNTRY_FLAGS.get("ireland", "🇮🇪")

        # Outside date range - return empty (could show UK flag or nothing)
        return ""

    # Default: return country flag
    return COUNTRY_FLAGS.get(country_lower, "")
