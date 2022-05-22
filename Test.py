from src.SchoolWare import SchoolWare
import json

SW = SchoolWare('XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX')
agenda = SW.get_agenda()
agenda = json.dumps(agenda, indent=2, ensure_ascii=False)

print(agenda)


