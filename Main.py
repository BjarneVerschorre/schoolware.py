import json
from datetime import datetime, timedelta
import requests
from rich import print as rprint

AA = 'F1A76D54-7A4B-4608-85B2-E38EC3A96D04'


def valid_token(token:str) -> bool:
    """ Checks if the token is valid """
    res = requests.get('https://vlot-leerlingen.durme.be/bin/server.fcgi/REST/myschoolwareaccount', cookies={'FPWebSession': token})
    return res.status_code == 200

def richify(text:str, colour:str) -> str:
    return f'[{colour}]{text}[/{colour}]'

def get_agenda(days:int = 7, rich:bool = False) -> dict:
    datum_vandaag = str(datetime.now()+timedelta(days=1)).split(' ')[0]
    datum_vandaag = datetime.strptime(datum_vandaag, "%Y-%m-%d")
    
    
    rooster = {}
    
    for dag in range(days):
        res = requests.get(f'https://vlot-leerlingen.durme.be/bin/server.fcgi/REST/AgendaPunt/?MinTot={datum_vandaag+timedelta(days=dag)}&MaxVan={datum_vandaag+timedelta(days=dag+1)}', cookies={'FPWebSession': AA})
        res_data = res.json()['data']

        datum = str(datum_vandaag+timedelta(days=dag)).split(' ')[0]
        rooster[datum] = {}

        for agenda_punt in res_data:
            if not 'W5IN' in agenda_punt['Groep']:
                continue

            
            vak_naam = agenda_punt['VakNaam']
            titel = agenda_punt['Titel']
            lokaal = agenda_punt['LokaalCode']
            type_punt = agenda_punt['TypePunt']
            van = agenda_punt['Van'].split(' ')[1]
            
            if type_punt > 2:
                titel = f'[{richify("TOETS", "bold red") if rich else "TOETS"}]: {titel}'


            if not van in rooster[datum]:
                rooster[datum][van] = {
                    'Vak': vak_naam,
                    'Onderwerp': 'Geen onderwerp',
                    'Lokaal': lokaal if lokaal else 'Geen lokaal',
                }
            else:
                pass

        
    return rooster 


def main():
    if not valid_token(AA):
        rprint(f'[[bold red]Failed[/bold red]] Invalid token!')
        exit(1)
    rprint(f'[[bold green]Success[/bold green]] Valid token!')

    agenda = get_agenda(1, True)
    
    rprint(json.dumps(agenda, indent=4))
    

if __name__ == '__main__':
    main()