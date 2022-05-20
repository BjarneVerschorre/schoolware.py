import json
from datetime import datetime
from SchoolWare import SchoolWare

SW = SchoolWare("554A2174-EF2F-46D5-A935-71CAC37A14F9", "W5IN")

agenda = SW.get_agenda(datetime(2022, 5, 19), datetime(2022, 5, 21))
print(json.dumps(agenda, indent=4))
