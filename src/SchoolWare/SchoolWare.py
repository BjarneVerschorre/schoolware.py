import json
from datetime import datetime, timedelta
import requests

class SchoolWare():
    def __init__(self, token:str) -> None:
        self.token = token
        if not self.__valid_token():
            raise ValueError("Token is invalid")  
        self._class = self.get_klas()

    __weekdays = ['maandag', 'dinsdag', 'woensdag', 'donderdag', 'vrijdag', 'zaterdag', 'zondag']
    

    def get_klas(self) -> str:
        res = self.__send_request(f'https://vlot-leerlingen.durme.be/bin/server.fcgi/REST/PuntenbladGrid?BeoordelingMomentVan={datetime.now()-timedelta(weeks=9)}&BeoordelingMomentTot={datetime.now()}')
        res_data = res.json()
        
        try:
            _class =  res_data['data'][0]['KlasCode']
        except KeyError:
            raise ValueError("Unable to find class")
        return _class
    
    def get_agenda(self, from_date:str = None, end_date:str = None) -> dict:
        """ Get the agenda for the given period """
        
        # If no date is given, use the current date, no week-ends 
        if from_date is None:
            from_date = datetime.now().date()
            from_weekday = self.__weekdays[from_date.weekday()]
            
            while self.__weekdays.index(from_weekday) > 4:
                from_date += timedelta(days=1)
                from_weekday = self.__weekdays[from_date.weekday()]
                
        else:
            from_date = datetime.strptime(from_date, "%Y-%m-%d")
            
        if end_date is None:
            end_date = from_date+timedelta(days=1)
        else:
            end_date = datetime.strptime(end_date, "%Y-%m-%d")
            
        res = self.__send_request(f'https://vlot-leerlingen.durme.be/bin/server.fcgi/REST/AgendaPunt/?MinTot={from_date}&&MaxVan={end_date}')
        if res.status_code != 200:
            raise ValueError("Unable to get agenda")
        
        res_data = res.json()['data']
        return self.__filter_agenda(res_data)
    
    def __filter_agenda(self, agenda:dict) -> dict:
        """ Filter the agenda to only show the current class """
        
        rooster = {}
        temp = {}
        
        for item in agenda:
            if not self._class in item['Groep']:
                continue
            
            item_date = item['Van'].split(' ')[0]
            vak_name = item['VakNaam']
            teacher_name = item['PersoneelNaam']
            lokaal = item['LokaalCode']
            start_time = item['Van'].split(' ')[1]
            end_time = item['Tot'].split(' ')[1]
            titel = item['Titel']
            commentaar = item['Commentaar']
            
            if not item_date in rooster:
                rooster[item_date] = {}
                
            les_uur = len(rooster[item_date])
            
            # Removing dublicates, needed because the API returns the same lesson multiple times (😬)
            if str(les_uur) in rooster[item_date]:
                if rooster[item_date][str(les_uur)]['van'] == start_time:
                    vorig_onderwerp = rooster[item_date][str(les_uur)]['onderwerp']
                    if vorig_onderwerp == 'Geen onderwerp' or vorig_onderwerp == "":
                        rooster[item_date][str(les_uur)]['onderwerp'] = self.__get_onderwerp(titel, commentaar, vak_name)
                    continue
                
                
            rooster[item_date][str(les_uur + 1)] = {
                'vak': vak_name,
                'onderwerp': self.__get_onderwerp(titel, commentaar, vak_name) or 'Geen onderwerp',
                'leerkracht': teacher_name,
                'lokaal': lokaal or 'Geen lokaal',
                'van': start_time,
                'tot': end_time,
            }
            temp[start_time] = str(les_uur)
            
        return rooster
        
    def __get_onderwerp(self, titel:str, commentaar:str, vak_name:str) -> str:
        onderwerp = ''
        if titel != vak_name:
            onderwerp = titel
            
        try:
            commentaar = json.loads(commentaar)['leerlingen']
        except json.decoder.JSONDecodeError:
            pass
        
        if onderwerp == '':
            onderwerp = commentaar
        else:
            onderwerp += ' ' + commentaar.replace('<br>', ' ').replace('\n', ' ')
        
        if onderwerp != '' and onderwerp[-1] == ' ':
            onderwerp = onderwerp[:-1]
        
        return onderwerp
    
    def get_information(self) -> dict:
        """ Get yours personal information from schoolware """
        return self.__send_request('https://vlot-leerlingen.durme.be/bin/server.fcgi/REST/myschoolwareaccount').json()
    
    def __valid_token(self) -> bool:
        """ Checks if the token is valid """
        res = self.__send_request('https://vlot-leerlingen.durme.be/bin/server.fcgi/REST/myschoolwareaccount')
        return res.status_code == 200

    def __send_request(self, url:str) -> requests.Response:
        return requests.get(url, cookies={'FPWebSession': self.token})

