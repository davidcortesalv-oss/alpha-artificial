# -*- coding: utf-8 -*-
"""
generar_univers_web.py — Passa l'univers d'inversió de config.py a la web
=========================================================================
La web necessita conèixer tots els actius (109 ETFs + 114 accions) per
ensenyar la galeria. En comptes de mantenir dues llistes a mà (que sempre
acaben desincronitzades), aquest script genera  web/univers.js  a partir
de config.py.

    python generar_univers_web.py

Executa'l cada cop que afegeixis o treguis un actiu de config.py.
"""

import os
import json
import config

RUTA = os.path.join("web", "univers.js")

# --- Descripción propia de cada empresa (lo que la gente reconoce) ---
# Si una empresa no está aquí, se usa la descripción genérica de su sector.
DESC_EMPRESA = {
    # EUA · Tecnologia
    "AAPL": "L'iPhone, el Mac i l'App Store. Una de les empreses més valuoses del món.",
    "MSFT": "Windows, Office, la núvol Azure i una aposta enorme per la IA.",
    "NVDA": "Els xips que fan funcionar la intel·ligència artificial. El gran guanyador del boom de la IA.",
    "GOOGL": "El cercador de Google, YouTube, Android i el model Gemini.",
    "AMZN": "La botiga en línia més gran del món i AWS, líder mundial en servidors al núvol.",
    "META": "Facebook, Instagram i WhatsApp: la companyia de xarxes socials més gran.",
    "TSLA": "Cotxes elèctrics, bateries i conducció autònoma. Molt volàtil.",
    "AMD": "Competidor directe de Nvidia i Intel en xips i processadors.",
    "INTC": "El fabricant de xips clàssic dels EUA, en plena reinvenció.",
    "AVGO": "Xips per a mòbils, xarxes i centres de dades. Gegant discret del sector.",
    "QCOM": "Els processadors i mòdems que porten la majoria de mòbils Android.",
    "CRM": "Salesforce: el programari amb què les empreses gestionen els seus clients.",
    "ORCL": "Bases de dades corporatives i infraestructura al núvol.",
    "ADBE": "Photoshop, Illustrator i el PDF. L'eina de tots els dissenyadors.",
    "IBM": "El veterà de la informàtica: serveis corporatius i computació quàntica.",
    "CSCO": "Els encaminadors i xarxes per on passa bona part d'internet.",
    "NFLX": "Netflix: streaming i producció pròpia de sèries i pel·lícules.",
    "PLTR": "Anàlisi massiva de dades per a governs i grans empreses.",
    # EUA · Salut
    "JNJ": "Farmacèutica gegant i productes de salut de consum.",
    "LLY": "Els fàrmacs contra l'obesitat i la diabetis que han disparat la companyia.",
    "PFE": "La farmacèutica de la vacuna de la covid.",
    "MRK": "Farmacèutica centrada en oncologia i vacunes.",
    "ABBV": "Immunologia i estètica mèdica (Botox).",
    "UNH": "L'asseguradora de salut més gran dels EUA.",
    "AMGN": "Biotecnològica veterana especialitzada en teràpies avançades.",
    "MRNA": "L'ARN missatger: vacunes de nova generació. Aposta d'alt risc.",
    # EUA · Finances
    "JPM": "El banc més gran dels Estats Units.",
    "BAC": "Bank of America: banca minorista i d'inversió.",
    "GS": "Goldman Sachs, la banca d'inversió per excel·lència.",
    "V": "Visa: cobra una comissió de gairebé cada pagament amb targeta del món.",
    "MA": "Mastercard, l'altre gran peatge dels pagaments globals.",
    "AXP": "American Express: targetes premium i clients d'alt poder adquisitiu.",
    "BRK-B": "El hòlding de Warren Buffett: assegurances, ferrocarrils i accions.",
    "PYPL": "PayPal: pagaments en línia arreu del món.",
    # EUA · Consum
    "KO": "Coca-Cola. La marca de begudes més reconeguda del planeta.",
    "PEP": "Pepsi, Lay's, Doritos i Gatorade.",
    "MCD": "McDonald's: menjar ràpid i, sobretot, un negoci immobiliari enorme.",
    "NKE": "Nike: roba i calçat esportiu.",
    "SBUX": "Starbucks: la cadena de cafeteries més gran del món.",
    "WMT": "Walmart, el supermercat més gran dels EUA.",
    "COST": "Costco: venda a l'engròs amb quota de soci.",
    "PG": "Ariel, Dodot, Gillette... productes que es compren passi el que passi.",
    "HD": "Home Depot: bricolatge i reformes de la llar.",
    "DIS": "Disney: pel·lícules, parcs temàtics i Disney+.",
    # EUA · Energia i indústria
    "XOM": "ExxonMobil, la petroliera més gran dels EUA.",
    "CVX": "Chevron: petroli i gas arreu del món.",
    "BA": "Boeing: avions comercials i defensa.",
    "CAT": "Caterpillar: maquinària de construcció i mineria.",
    "GE": "General Electric: turbines d'avió i energia.",
    "LMT": "Lockheed Martin: caces F-35 i sistemes de defensa.",
    "RTX": "Motors d'avió i míssils. Indústria de defensa pesant.",
    "DE": "John Deere: la maquinària agrícola verda de tota la vida.",
    "UPS": "Paqueteria i logística mundial.",
    # EUA · Altres
    "T": "AT&T: telefonia i internet als Estats Units.",
    "VZ": "Verizon, l'altra gran teleco americana.",
    "UBER": "Uber: transport de persones i repartiment de menjar.",
    "ABNB": "Airbnb: allotjaments turístics d'particulars.",
    "COIN": "Coinbase: la borsa de criptomonedes cotitzada. Molt volàtil.",
    "F": "Ford: cotxes, pickups i transició a l'elèctric.",
    "GM": "General Motors: Chevrolet, Cadillac i vehicles elèctrics.",
    # Espanya i Catalunya
    "ITX.MC": "Zara, Bershka i Massimo Dutti. La joia de la corona espanyola.",
    "SAN.MC": "Banco Santander: el banc espanyol més internacional.",
    "BBVA.MC": "BBVA: banca a Espanya, Mèxic i Turquia.",
    "IBE.MC": "Iberdrola: electricitat i lideratge mundial en renovables.",
    "TEF.MC": "Telefónica (Movistar): telefonia a Espanya i Llatinoamèrica.",
    "REP.MC": "Repsol: refineries, benzineres i energia.",
    "GRF.MC": "Empresa CATALANA líder mundial en medicaments derivats del plasma.",
    "CLNX.MC": "Empresa CATALANA propietària de torres de telecomunicacions per tota Europa.",
    "FER.MC": "Ferrovial: autopistes i aeroports arreu del món.",
    "AENA.MC": "Aena: gestiona tots els aeroports espanyols, inclòs el Prat.",
    "ELE.MC": "Endesa: una de les grans elèctriques espanyoles.",
    "AMS.MC": "Amadeus: la tecnologia darrere de la majoria de reserves de vols.",
    # França
    "MC.PA": "LVMH: Louis Vuitton, Dior i Moët. El gegant del luxe.",
    "RMS.PA": "Hermès: els bosses Birkin i el luxe més exclusiu.",
    "OR.PA": "L'Oréal: cosmètica número u del món.",
    "AIR.PA": "Airbus: el rival europeu de Boeing.",
    "TTE.PA": "TotalEnergies: petroli, gas i renovables.",
    "SAN.PA": "Sanofi: farmacèutica francesa i vacunes.",
    "BNP.PA": "BNP Paribas: el banc més gran de la zona euro.",
    "CAP.PA": "Capgemini: consultoria i serveis tecnològics.",
    # Alemanya
    "SAP.DE": "SAP: el programari de gestió de les grans empreses europees.",
    "SIE.DE": "Siemens: automatització industrial, trens i tecnologia mèdica.",
    "ALV.DE": "Allianz: una de les asseguradores més grans del món.",
    "BMW.DE": "BMW: cotxes premium i Mini.",
    "MBG.DE": "Mercedes-Benz: automoció de gamma alta.",
    "ADS.DE": "Adidas: el rival europeu de Nike.",
    "DTE.DE": "Deutsche Telekom, propietària de T-Mobile.",
    "BAS.DE": "BASF: la química més gran del món.",
    # Països Baixos, Bèlgica, Itàlia
    "ASML.AS": "Fabrica les úniques màquines del món capaces de gravar els xips més avançats. Peça clau del planeta.",
    "ADYEN.AS": "Adyen: la passarel·la de pagaments d'Uber, Spotify i eBay.",
    "PHIA.AS": "Philips: equipament mèdic i salut personal.",
    "ABI.BR": "AB InBev: Estrella, Corona, Budweiser... la cervesera més gran.",
    "RACE": "Ferrari: cotxes esportius de luxe amb marges altíssims.",
    "ENI.MI": "Eni: la petroliera italiana.",
    "ISP.MI": "Intesa Sanpaolo: el gran banc italià.",
    "STLAM.MI": "Stellantis: Peugeot, Fiat, Citroën, Jeep i Opel.",
    # Suïssa
    "NESN.SW": "Nestlé: Nespresso, KitKat i Purina. Consum bàsic mundial.",
    "NOVN.SW": "Novartis: farmacèutica suïssa de primer nivell.",
    "UBSG.SW": "UBS: banca privada i gestió de grans fortunes.",
    # Regne Unit
    "SHEL.L": "Shell: una de les petrolieres més grans del món.",
    "BP.L": "BP: petroli, gas i transició energètica.",
    "AZN.L": "AstraZeneca: oncologia i la vacuna de la covid.",
    "HSBA.L": "HSBC: banca global amb molt de pes a Àsia.",
    "ULVR.L": "Unilever: Dove, Magnum, Hellmann's i Frigo.",
    "RIO.L": "Rio Tinto: mineria de ferro, coure i liti.",
    # Àsia i emergents
    "TSM": "Fabrica físicament els xips de Nvidia i Apple. L'empresa més estratègica d'Àsia.",
    "7203.T": "Toyota: el fabricant de cotxes més gran del món.",
    "6758.T": "Sony: PlayStation, càmeres, música i cinema.",
    "005930.KS": "Samsung: mòbils, televisors i memòries. Gegant coreà.",
    "BABA": "Alibaba: el comerç electrònic i el núvol de la Xina.",
    "PDD": "PDD, propietària de Temu: comerç ultrabarat en expansió mundial.",
    "NTES": "NetEase: videojocs i música en línia a la Xina.",
    "INFY": "Infosys: serveis informàtics des de l'Índia per a mig món.",
    "HDB": "HDFC Bank: el banc privat més gran de l'Índia.",
}

# --- Descripciones cortas por sector (respaldo si falta la propia) ---
DESC_SECTOR = {
    "Tecnologia": "Empresa tecnològica.",
    "Semiconductors": "Fabricant de xips: el maquinari que fa funcionar la IA.",
    "Salut": "Sector sanitari: farmacèutiques, biotecnologia o equipament mèdic.",
    "Finances": "Banca, assegurances o mitjans de pagament.",
    "Consum": "Ven productes o serveis directament a la gent.",
    "Energia": "Petroli, gas o electricitat.",
    "Indústria": "Fabricació, maquinària o infraestructures.",
    "Automoció": "Fabricant de vehicles.",
    "Luxe": "Marques de luxe: moda, joieria i alta gamma.",
    "Telecomunicacions": "Xarxes de telefonia i internet.",
    "Mitjans": "Entreteniment, streaming o mitjans de comunicació.",
    "Defensa": "Indústria aeroespacial i de defensa.",
    "Logística": "Transport i distribució de mercaderies.",
    "Química": "Indústria química i de materials.",
    "Mineria": "Extracció de minerals i metalls.",
}

# --- Qué dibujo (art SVG) toca a cada sector de acciones ---
ART_SECTOR = {
    "Tecnologia": "tech", "Semiconductors": "ai", "Salut": "health",
    "Finances": "finance", "Consum": "consumer", "Energia": "energy",
    "Indústria": "industry", "Automoció": "auto", "Luxe": "luxe",
    "Telecomunicacions": "media", "Mitjans": "media", "Defensa": "defense",
    "Logística": "airline", "Química": "industry", "Mineria": "copper",
}

# --- Nivel de riesgo orientativo por sector (1 tranquilo – 5 movido) ---
RISC_SECTOR = {
    "Tecnologia": 4, "Semiconductors": 5, "Salut": 3, "Finances": 4,
    "Consum": 2, "Energia": 4, "Indústria": 3, "Automoció": 4,
    "Luxe": 3, "Telecomunicacions": 2, "Mitjans": 4, "Defensa": 3,
    "Logística": 3, "Química": 3, "Mineria": 4,
}

BANDERES = {
    "EUA": "🇺🇸", "Espanya": "🇪🇸", "Catalunya": "🏴", "França": "🇫🇷",
    "Alemanya": "🇩🇪", "Itàlia": "🇮🇹", "Països Baixos": "🇳🇱",
    "Bèlgica": "🇧🇪", "Suïssa": "🇨🇭", "Regne Unit": "🇬🇧", "Japó": "🇯🇵",
    "Xina": "🇨🇳", "Índia": "🇮🇳", "Taiwan": "🇹🇼", "Corea del Sud": "🇰🇷",
}


def main():
    # Las descripciones ricas de los ETFs ya están escritas a mano en
    # web/etfs.js; aquí solo generamos las ACCIONES y la lista de categorías.
    accions = {}
    for tk, (nom, sector, pais, moneda) in config.UNIVERS_ACCIONS.items():
        accions[tk] = {
            "nom": nom,
            "cat": sector,
            "art": ART_SECTOR.get(sector, "generic"),
            "risc": RISC_SECTOR.get(sector, 3),
            "desc": DESC_EMPRESA.get(tk) or DESC_SECTOR.get(sector, "Empresa cotitzada."),
            "tipus": "accio",
            "pais": pais,
            "bandera": BANDERES.get(pais, "🌍"),
            "moneda": moneda,
        }

    sectors = sorted({d["cat"] for d in accions.values()})
    paisos = sorted({d["pais"] for d in accions.values()})

    os.makedirs("web", exist_ok=True)
    with open(RUTA, "w", encoding="utf-8") as f:
        f.write("/* =====================================================================\n")
        f.write("   ALPHA ARTIFICIAL — univers.js  (GENERAT AUTOMÀTICAMENT)\n")
        f.write("   ---------------------------------------------------------------------\n")
        f.write("   NO EDITIS AQUEST FITXER A MÀ: es genera des de config.py amb\n")
        f.write("       python generar_univers_web.py\n")
        f.write("   ===================================================================== */\n")
        f.write("(function () {\n  \"use strict\";\n\n")
        f.write("  window.ALPHA_ACCIONS = ")
        f.write(json.dumps(accions, ensure_ascii=False, indent=2).replace("\n", "\n  "))
        f.write(";\n\n")
        f.write("  window.ALPHA_SECTORS = ")
        f.write(json.dumps(sectors, ensure_ascii=False))
        f.write(";\n")
        f.write("  window.ALPHA_PAISOS = ")
        f.write(json.dumps(paisos, ensure_ascii=False))
        f.write(";\n})();\n")

    print(f"[OK] Escrit {RUTA} amb {len(accions)} accions de {len(paisos)} països.")


if __name__ == "__main__":
    main()
