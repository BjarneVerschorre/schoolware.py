from src.SchoolWare import SchoolWare
import json

SW = SchoolWare('8ABC8C6A-8FAB-4AB4-AD7A-98249692588E')
agenda = SW.get_agenda()
agenda = json.dumps(agenda, indent=2)

print(agenda)


