
from bs4 import BeautifulSoup
from time import sleep
import datetime as dt
import pandas as pd
import numpy as np
import requests
import locs

class Finn:

    def __init__(self, sted = None, brukt_bolig = None, leilighet = False, rekkehus = False, enebolig = False, tomannsbolig = False, show_progress_bar = False, tot_listings = None, file_name = None,
                 save_cols = ['url', 'Adresse', 'Postnr', 'Fylke', 'Sted', 'Boligtype', 'Eieform', 'Prisantydning', 'Totalpris', 'Bruksareal','Kvm pris', 'Rom', 'Omkostninger', 'Tinglyst', 'Pris ss', 'Sist endret']):

        self.start_time = 0
        self.runtime()

        # Creating a url using the function ( self.create_url() )
        self.url = self.create_url(
            is_new_property=brukt_bolig,
            is_apartment = leilighet,
            is_terraced_house = rekkehus,
            is_detached_house = enebolig,
            is_semi_detached_house = tomannsbolig)
        self.urls = []

        self.locations_ = sted
        self.locations = self.loc_checker(sted = sted)

        # Obtaining list with valid proxies
        self.valid_proxies = self.get_valid_proxies()

        # Creating a dict to store data in called (self.data)
        self.data = {
            'url': [],
            'Adresse': [],
            'Postnr': [],
            'Fylke': [],
            'Sted': [],
            'Prisantydning': [],
            'Totalpris': [],
            'Omkostninger': [],
            'Fellesgjeld': [],
            'Felleskost/mnd.': [],
            'Kommunale avg.': [],
            'Eiendomsskatt': [],
            'Formuesverdi': [],
            'Boligtype': [],
            'Eieform': [],
            'Soverom': [],
            'Rom': [],
            'Etasje': [],
            'Primærrom': [],
            'Bruksareal': [],
            'Byggeår': [],
            'Energimerking': [],
            'Tomteareal': [],
            'Tinglyst': [],
            'Pris ss': [],
            'Sist endret': []
            }

        # Creating a dict which hold the dtypes for our dataframe which is used to save data
        self.dtypes = {
            'url': 'str',
            'Adresse': 'str',
            'Postnr': 'str',
            'Fylke': 'str',
            'Sted': 'str',
            'Prisantydning': 'int',
            'Totalpris': 'int',
            'Omkostninger': 'int',
            'Fellesgjeld': 'int',
            'Felleskost/mnd.': 'int',
            'Kommunale avg.': 'str',
            'Eiendomsskatt': 'str',
            'Formuesverdi': 'int',
            'Boligtype': 'str',
            'Eieform': 'str',
            'Soverom': 'int',
            'Rom': 'int',
            'Etasje': 'int',
            'Primærrom': 'int',
            'Bruksareal': 'int',
            'Byggeår': 'str',
            'Energimerking': 'str',
            'Tomteareal': 'int',
            'Tinglyst': 'object',
            'Pris ss': 'int',
            'Sist endret': 'str'
        }

        # Creating a dict that contains 'None' values for each key in self.data  
        self.data_none = {
            'url': '',
            'Adresse': '',
            'Postnr': '',
            'Fylke': '',
            'Sted': '',
            'Prisantydning': 0,
            'Totalpris': 0,
            'Omkostninger': 0,
            'Fellesgjeld': 0,
            'Felleskost/mnd.': 0,
            'Kommunale avg.': '',
            'Eiendomsskatt': '',
            'Formuesverdi': 0,
            'Boligtype': '',
            'Eieform': '',
            'Soverom': 0,
            'Rom': 0,
            'Etasje': 0,
            'Primærrom': 0,
            'Bruksareal': 0,
            'Byggeår': 0,
            'Energimerking': '',
            'Tomteareal': 0,
            'Tinglyst': '',
            'Pris ss': 0,
            'Sist endret': ''
            }

        # Creating a list that holds alle the keys in dict self.data
        self.datakeys = self.data.keys()

        # A list containing columns that will be saved to the excel file
        self.save_cols = save_cols

        # A list that contains strings that we want to replace when cleaning data
        self.chars = [',−', ' m²', ' kr', ' (eiet)', 'Eier ', '\xa0', '(', ')', 'festet']
        
        self.months = {
            'jan': 1, 
            'feb': 2, 
            'mars': 3, 
            'april': 4, 
            'mai': 5, 
            'jun': 6, 
            'jul': 7, 
            'aug': 8, 
            'sep': 9, 
            'okt': 10, 
            'nov': 11, 
            'des': 12
            }

        self.tot_listings = tot_listings

        self.file_name = file_name

        self.show_progress_bar = show_progress_bar
        if self.show_progress_bar:
            import colorama as clrm
            self.color_yellow = clrm.Fore.LIGHTYELLOW_EX
            self.color_green  = clrm.Fore.LIGHTGREEN_EX
            self.color_white  = clrm.Fore.WHITE

    def runtime(self):
        
        if self.start_time == 0:
            self.start_time = dt.datetime.now()

        elif self.start_time != 0:
            end_time = dt.datetime.now()
            print(f'\nExecution Time: {end_time - self.start_time}\n')

    def progress_bar(self, progress, total):

        if self.show_progress_bar:
            percent = 100 * (progress / float(total))
            bar = '█' * int(percent) + '-' * (100 - int(percent))
            
            if progress < total:
                print(self.color_yellow + f'\r┃{bar}┃ {percent:.2f}% ┃ {progress} of total {total}', end = '\r')
            else:
                print(self.color_green + f'\r┃{bar}┃ {percent:.2f}% ┃ {progress} of total {total}' + self.color_white + '\n', end = '\r')

    def terminal_print(self, text, tot_len = 50):
        len_diff = tot_len - len(text)
        text_to_print = text + ' ' * len_diff
        print(f'\r{text_to_print}', end = '\r')
        
    def create_url(self,
                   is_new_property, 
                   is_apartment, 
                   is_terraced_house, 
                   is_detached_house, 
                   is_semi_detached_house):

        url = 'https://www.finn.no/realestate/homes/search.html?'

        # adding properties to url
        url = self.add_prpoerties(url, is_new_property, is_apartment, is_terraced_house, is_detached_house, is_semi_detached_house)

        return url

    def loc_checker(self, sted):

        loc_list = []
        loc_keys = locs.locations.keys()

        for location in sted:
            loc_id = locs.locations[location]
            
            if location in loc_list:
                pass

            elif loc_id[9] == '0':
                loc_id = f'location=1{loc_id[10:]}'

                for key in loc_keys:
                    
                    if loc_id == locs.locations[key][:16]:
                        loc_list.append(key)

            else: 
                loc_list.append(location)

        print(loc_list)
        return loc_list

    def get_valid_proxies(self):

        PATH_PROXIES = '/Users/johnasp/Desktop/vsc/creFin/valid_proxies.txt'

        with open(PATH_PROXIES, 'r') as f:
            proxies = f.read().split('\n')
        
        return proxies

    def add_prpoerties(self, url,
                       is_new_property, 
                       is_apartment, 
                       is_terraced_house, 
                       is_detached_house, 
                       is_semi_detached_house):
        
        if is_new_property is False: # Bruktbolig
            url += 'is_new_property=false'

        elif is_new_property is True: # Nybygg
            url += 'is_new_property=true'

        if is_detached_house is True: # Enebolig
            url += '&property_type=1'

        if is_semi_detached_house is True: # Tomansbolig
            url += '&property_type=2'

        if is_apartment is True: # Leilighet
            url += '&property_type=3'

        if is_terraced_house is True: # Rekkehus
            url += '&property_type=4'
        
        return url

    def round_up(self, numb):

        numbr = round(numb)
        if numbr < numb:
            return numbr + 1
        else: 
            return numbr

    def get_listings(self, url, sted):

        page = requests.get(url = url)
        soup = BeautifulSoup(page.text, features = 'lxml')

        tot_listings = soup.find_all('span', class_ = 'font-bold')
        tot_listings = int(self.replace_char(tot_listings[6].text, chars = self.chars))
        if self.tot_listings is not None and self.tot_listings < tot_listings:
            tot_listings = self.tot_listings 

        # max 50 pages on finn.no
        pages = self.round_up(tot_listings / 50)
        # self.terminal_print(text = f'Total Listings in [{sted}]: {tot_listings} Total Pages: {pages}')
        print(f'Total Listings in [{sted}]: {self.color_yellow}{tot_listings}{self.color_white}\t Total Pages: {pages}')

        sorting_alternatives = ['&sort=PRICE_SQM_DESC', '&sort=PRICE_SQM_ASC', '&sort=RELEVANCE', '&sort=AREA_PROM_DESC', '&sort=AREA_PROM_ASC', '&sort=PRICE_ASKING_DESC', '&sort=PRICE_ASKING_ASC', '&sort=PUBLISHED_DESC', '&sort=PRICE_DESC', '&sort=PRICE_ASC']

        urls_collected = []

        for alternative in sorting_alternatives:
            
            if len(urls_collected) >= tot_listings :
                self.terminal_print(text = f'Total URLs collected in [{sted}]: {self.color_green}{len(urls_collected)}{self.color_white}' + '\n')
                return urls_collected

            # checking number of pages
            if pages > 50:
                x = 50
            else:
                x = pages

            # scraping listings_urls for each page in the sorting alternative
            for page in range(1, x + 1):

                sleep(0.5)                

                ny_url = url + alternative + f'&page={page}'

                page = requests.get(url = ny_url)
                soup = BeautifulSoup(page.text, features = 'lxml')

                listings_section = soup.find('section', attrs={'id': 'page-results'})
                listings = listings_section.find_all('a')[1:]

                # collecting listing urls
                for listing in listings:

                    href = listing['href']
                    
                    if href not in urls_collected and len(urls_collected) < tot_listings:
                        urls_collected.append(href), self.urls.append(href)
                    else:
                        break
                    
                self.terminal_print(text = f'Total URLs collected in [{sted}]: {self.color_yellow}{len(urls_collected)}{self.color_white}')

    def replace_char(self, value, chars):

        for char in chars:
            value = str(value).replace(char, '')

        return value

    def extract_adresse(self, soup):

        full_adresse = str(soup.find(attrs={'data-testid': 'object-address'}).text)

        try:
            
            if full_adresse.find(',') > 0:
                full_adresse = full_adresse.split(',')
                adresse = full_adresse[0].strip()
                postnr = full_adresse[-1][1:5].strip()
                fylke = full_adresse[-1][5:].strip()
        
                return adresse, postnr, fylke
        
        except:
            pass

        try:
            adresse = None
            postnr = full_adresse[0:4].strip()
            fylke = full_adresse[4:].strip()
            return adresse, postnr, fylke

        except:
            return None, None, None
 
    def extract_titler_verdier(self, soup):

        titler = soup.find_all('dt', class_ = 'm-0')
        verdier = soup.find_all('dd', class_ = 'm-0 font-bold')

        titler = [tittel.text for tittel in titler]
        verdier = [self.replace_char(value = verdi.text, chars = self.chars) for verdi in verdier]

        return titler, verdier

    def previous_sale(self, url):

        page2 = requests.get(url = url)
        soup2 = BeautifulSoup(page2.text, features = 'lxml')

        siste_salg = soup2.find_all('tr')[1].find_all('td')

        tinglyst = self.replace_char(siste_salg[0].text, chars = self.chars).split('.')
        tinglyst = [int(verdi) for verdi in tinglyst]

        tinglyst_dt = dt.date(tinglyst[2], tinglyst[1], tinglyst[0])

        pris = self.replace_char(siste_salg[-1].text, chars = self.chars)

        return tinglyst_dt, pris

    def latest_change(self, soup):
        sist_endret = soup.find_all('td', class_ = 'pl-8')[1].text
        h, m = sist_endret[-5:].split(':') # timer og minutter
        d, mnd, y, blank = [x.replace('.', '').strip() for x in sist_endret[:-5].split(' ')] # År, måned og dag
        mnd = self.months[mnd]
        return dt.datetime(year = int(y), month = int(mnd), day = int(d), hour = int(h), minute = int(m))

    def scrape_listings(self):

        for sted in self.locations:

            url_sted = f'{self.url}&{locs.locations[sted]}'

            print(f'\nCollecting URLs for listings in [{sted}]')
            
            urls = self.get_listings(url = url_sted, sted = sted)

            print(f'\nScraping listings in [{sted}]')
            self.progress_bar(progress = 0, total = len(urls))

            save_d = 0

            for x, url in enumerate(iterable = urls, start = 1):
                
                sleep(0.5)
                self.scrape_listing(url = url, sted = sted)
                save_d += 1

                if save_d == 5:
                    save_d = 0
                    self.save_data()
                    self.progress_bar(progress = x, total = len(urls))
        
            self.progress_bar(progress = x, total = len(urls))

        self.save_data()
        print('\nData Saved!')
        print(self.df.head())
        # print(self.df.describe().astype('int64'))

    def scrape_listing(self, url, sted):

        try:
            # scrape listing 
            page = requests.get(url = url)
            soup = BeautifulSoup(page.text, features = 'lxml')

            # collect data
            titler, verdier = self.extract_titler_verdier(soup = soup)

            titler.append('url'), verdier.append(url)

            adresse, postnr, fylke = self.extract_adresse(soup = soup)
            titler.extend(['Adresse', 'Postnr', 'Fylke', 'Sted']), verdier.extend([adresse, postnr, fylke, sted])

            try:
                href = soup.find('a', attrs={'data-testid': 'ownership-history-link'})['href']
                url_tidl_solgt = 'https://www.finn.no' + href

                # info from previous sale
                tinglyst_dt, pris = self.previous_sale(url = url_tidl_solgt)

                titler.extend(['Tinglyst', 'Pris ss']), verdier.extend([tinglyst_dt, pris])

            except:
                pass

            try:
                prisantydning = soup.find('span', class_ = 'text-28 font-bold').text
                prisantydning = self.replace_char(prisantydning, chars = self.chars)
                titler.append('Prisantydning'), verdier.append(prisantydning)

            except:
                pass

            try:
                sist_endret = self.latest_change(soup = soup)
                titler.append('Sist endret'), verdier.append(sist_endret)

            except:
                pass

            self.data_collector(titler = titler, verdier = verdier)
        
        except:
            # print('Did not scrape listing successfully...')
            pass

    def make_hyperlink(self, url):
        return f'=HYPERLINK("{url}", "Klikk her - Finn Annonse")'

    def data_collector(self, titler, verdier):

        for key in self.datakeys:

            if key in titler:
                pos = titler.index(key)
                self.data[key].append(verdier[pos])

            else:
                self.data[key].append(self.data_none[key])     

    def create_file_name(self):

        if self.file_name is None:
            name = ''
            for sted in self.locations_:
                name += f'{str(sted).lower()}_'
        
        else:
            name = self.file_name
        return '/Users/johnasp/Desktop/vsc/creFin/scraped_data/' + name + 'annonser.xlsx'
            
    def save_data(self):
        
        # Creating a dataframe out of the collected data (stored in dict self.data)

        self.df = pd.DataFrame(data = self.data)
        # print(self.df.tail(20))

        # Setting datatypes for each column (stored in dict self.dtypes)
        self.df = self.df.astype(self.dtypes)

        # Create Column (Kvm Pris)
        self.df['Kvm pris'] = self.df['Totalpris'] / self.df['Bruksareal']
        self.df['kvm pris'] = self.df['Kvm pris'].replace([np.NaN, np.nan, np.inf, -np.inf], 0, inplace = True)
        self.df['Kvm pris'] = self.df['Kvm pris'].astype('int')

        # making column (url) clickable
        self.df['url'] = self.df['url'].apply(self.make_hyperlink)

        # Create dataframe with selected columns (columns keys stored in self.save_cols)
        self.df = self.df[self.save_cols]

        path = self.create_file_name()
        boligtyper = ['Leilighet', 'Rekkehus', 'Enebolig', 'Tomannsbolig']

        with pd.ExcelWriter(path = path) as writer:
            self.df.to_excel(writer, sheet_name = 'FINN.ANNONSER', index = False)

            for boligtype in boligtyper:
                
                self.df_stat = self.df.loc[self.df['Boligtype'] == boligtype]

                for n, x in enumerate([0, 11, 22, 33, 44, 55, 66], start=1):

                    self.df_stat_w = self.df_stat.loc[self.df_stat['Rom'] == n]
                    self.df_stat_w = self.df_stat_w.describe()
                    self.df_stat_w.name = f'{x}-roms {boligtype}'
                    self.df_stat_w = self.df_stat_w[['Prisantydning', 'Totalpris', 'Bruksareal', 'Kvm pris']]
                    self.df_stat_w.to_excel(writer, sheet_name = boligtype, startrow = x, startcol = 0)


if __name__ == '__main__':
    
    finn = Finn(
        sted = ['Oslo'],
        brukt_bolig = False,
        leilighet = True,
        enebolig = True,
        tomannsbolig = True,
        rekkehus = True,
        show_progress_bar = True,
        file_name = 'tester',
        tot_listings = 200)

    finn.scrape_listings()

    finn.runtime()


### --- Steder [sted] ---

# Agder 
#   - [Arendal, Birkenes, Bygland, Bykle, Evje og Hornnes, Farsund, Flekkefjord, Froland, Gjerstad, Grimstad, Hægebostad, Iveland, Kristiansand, Kvinesdal, Lillesand, Lindesnes, Lyngdal, Risør, Sirdal, Tvedestrand, Valle, Vegårshei, Vennesla, Åmli, Åseral]
# Innlander 
#   - [Alvdal, Dovre, Eidskog, Elverum, Engerdal, Etnedal, Gausdal, Gjøvik, Gran, Grue, Hamar, Kongsvinger, Lesja, Lillehammer, Lom, Løten, Nord-Aurdal, Nord-Fron, Nord-Odal, Nordre Land, Os, Rendalen, Ringebu, Ringsaker, Sel, Skjåk, Stange, Stor-Elvdal, Søndre Land, Sør-Aurdal, Sør-Fron, Sør-Odal, Tolga, Trysil, Tynset, Vang, Vestre Slidre, Vestre Toten, Vågå, Våler, Åmot, Åsnes, Østre Toten, Øyer, Øystre Slidre]
# Møre og Romsdal 
#   - [Aukra, Aure, Averøy, Fjord, Giske, Gjemnes, Hareid, Herøy, Hustadvika, Kristiansund, Molde, Rauma, Sande, Smøla, Stranda, Sula, Sunndal, Surnadal, Sykkylven, Tingvoll, Ulstein, Vanylven, Vestnes, Volda, Ålesund, Ørsta]
# Nordland 
#   - [Alstahaug, Andøy, Beiarn, Bindal, Bodø, Brønnøy, Bø, Dønna, Evenes, Fauske, Flakstad, Gildeskål, Grane, Hadsel, Hamarøy, Hattfjelldal, Hemnes, Herøy, Leirfjord, Lurøy, Lødingen, Meløy, Moskenes, Narvik, Nesna, Rana, Rødøy, Røst, Saltdal, Sortland, Steigen, Sømna, Sørfold, Træna, Vefsn, Vega, Vestvågøy, Vågan, Værøy, Øksnes]
# Oslo 
#   - [Bjerke, Bygdøy - Frogner, Bøler, Ekeberg - Bekkelaget, Furuset, Gamle Oslo, Grefsen - Kjelsås, Grorud, Grünerløkka - Sofienberg, Hellerud, Helsfyr - Sinsen, Lambertseter, Manglerud, Nordstrand, Romsås, Røa, Sagene - Torshov, Sentrum, Sogn, St.Hanshaugen - Ullevål, Stovner, Søndre Nordstrand, Ullern, Uranienborg - Majorstuen, Vinderen, Østensjø]
# Rogaland 
#   - [Bjerkreim, Bokn, Eigersund, Gjesdal, Haugesund, Hjelmeland, Hå, Karmøy, Klepp, Kvitsøy, Lund, Randaberg, Sandnes, Sauda, Sokndal, Sola, Stavanger, Strand, Suldal, Time, Tysvær, Vindafjord]
# Svalbard 
#   - [Alta, Balsfjord, Bardu, Berlevåg, Båtsfjord, Dyrøy, Gamvik, Gratangen, Hammerfest, Harstad, Hasvik, Ibestad, Karasjok, Karlsøy, Kautokeino, Kvæfjord, Kvænangen, Kåfjord, Lebesby, Loppa, Lyngen, Målselv, Måsøy, Nesseby, Nordkapp, Nordreisa, Porsanger, Salangen, Senja, Skjervøy, Storfjord, Sør-Varanger, Sørreisa, Tana, Tjeldsund, Tromsø, Vadsø, Vardø]
# Troms og Finnmark 
#   - [Flatanger, Frosta, Frøya, Grong, Heim, Hitra, Holtålen, Høylandet, Inderøy, Indre Fosen, Leka, Levanger, Lierne, Malvik, Melhus, Meråker, Midtre Gauldal, Namsos, Namsskogan, Nærøysund, Oppdal, Orkland, Osen, Overhalla, Rennebu, Rindal, Røros, Røyrvik, Selbu, Skaun, Snåsa, Steinkjer, Stjørdal, Trondheim, Tydal, Verdal, Åfjord, Ørland]
# Trøndelag 
#   - [Bamble, Drangedal, Fyresdal, Færder, Hjartdal, Holmestrand, Horten, Kragerø, Kviteseid, Larvik, Midt-Telemark, Nissedal, Nome, Notodden, Porsgrunn, Sandefjord, Seljord, Siljan, Skien, Tinn, Tokke, Tønsberg, Vinje]
# Vestfold og Telemark 
#   - [Alver, Askvoll, Askøy, Austevoll, Austrheim, Bergen, Bjørnafjorden, Bremanger, Bømlo, Etne, Fedje, Fitjar, Fjaler, Gloppen, Gulen, Hyllestad, Høyanger, Kinn, Kvam, Kvinnherad, Luster, Lærdal, Modalen, Osterøy, Sogndal, Solund, Stad, Stord, Stryn, Sunnfjord, Sveio, Tysnes, Ullensvang, Ulvik, Vaksdal, Vik, Voss, Årdal, Øygarden]
# Vestland 
#   - [Aremark, Asker, Aurskog-Høland, Bærum, Drammen, Eidsvoll, Enebakk, Flesberg, Flå, Fredrikstad, Frogn - Drøbak, Gjerdrum, Gol, Halden, Hemsedal, Hol, Hole, Hurdal, Hvaler, Indre Østfold, Jevnaker, Kongsberg, Krødsherad, Lier, Lillestrøm, Lunner, Lørenskog, Marker, Modum, Moss, Nannestad, Nes, Nesbyen, Nesodden, Nittedal, Nordre Follo, Nore og Uvdal, Rakkestad, Ringerike, Rollag, Råde, Rælingen, Sarpsborg, Sigdal, Skiptvet, Ullensaker, Vestby, Våler, Ål, Ås, Øvre Eiker]