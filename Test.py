from src.SchoolWare import SchoolWare
import json

SW = SchoolWare('69812F9C-9673-4780-971D-6353B55BEBFA')
agenda = SW.get_agenda()
agenda = json.dumps(agenda, indent=2, ensure_ascii=False)

print(agenda)


