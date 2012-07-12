from collections import OrderedDict

class Building:
  def __init__(self, name):
    self.name = name
    self.floors = OrderedDict()

class Floor:
  def __init__(self, name, map = None):
    self.name = name
    self.map = map
    self.zones = OrderedDict()

class Zone:
  def __init__(self, name, coord, controls):
    self.name = name
    self.coord = coord
    self.controls = controls

def lookup(building, floor = None, zone = None):
  if (building not in buildings):
    return None
  b = buildings[building]

  if (floor != None):
    if (floor not in b.floors):
      return None
    f = b.floors[floor]

    if (zone != None):
      if (zone not in f.zones):
        return None
      z = f.zones[zone]
      return (b, f, z)
    else:
      return (b, f)
  else:
    return b

buildings = OrderedDict()

buildings['SutardjaDaiHall'] = Building('Sutardja Dai Hall')

buildings['SutardjaDaiHall'].floors['Floor2'] = \
  Floor('Floor 2')

buildings['SutardjaDaiHall'].floors['Floor3'] = \
  Floor('Floor 3')

buildings['SutardjaDaiHall'].floors['Floor4'] = \
  Floor('Floor 4', '4thFloor.png')

buildings['SutardjaDaiHall'].floors['Floor5'] = \
  Floor('Floor 5', '5thFloor.png')

buildings['SutardjaDaiHall'].floors['Floor6'] = \
  Floor('Floor 6', '6thFloor.png')

buildings['SutardjaDaiHall'].floors['Floor7'] = \
  Floor('Floor 7', '7thFloor.png')


buildings['SutardjaDaiHall'].floors['Floor4'].zones['Zone1'] = \
  Zone('Zone 1',
       '0, 88, 95, 240', 
       {'dev' : 'WS86007', 'high' : 'RELAY11', 'low' : 'RELAY12'})

buildings['SutardjaDaiHall'].floors['Floor4'].zones['Zone2'] = \
  Zone('Zone 2',
       '95, 88, 195, 202', 
       {'dev' : 'WS86007', 'high' : 'RELAY09', 'low' : 'RELAY10'})

buildings['SutardjaDaiHall'].floors['Floor4'].zones['Zone3'] = \
  Zone('Zone 3',
       '195, 88, 365, 202', 
       {'dev' : 'WS86007', 'high' : 'RELAY07', 'low' : 'RELAY08'})

buildings['SutardjaDaiHall'].floors['Floor4'].zones['Zone4'] = \
  Zone('Zone 4',
       '365, 88, 515, 202', 
       {'dev' : 'WS86007', 'high' : 'RELAY03', 'low' : 'RELAY04'})

buildings['SutardjaDaiHall'].floors['Floor4'].zones['Zone5'] = \
  Zone('Zone 5',
       '515, 88, 599, 240', 
       {'dev' : 'WS86007', 'high' : 'RELAY05', 'low' : 'RELAY06'})

# 5th Floor
buildings['SutardjaDaiHall'].floors['Floor5'].zones['Zone1'] = \
  Zone('Zone 1',
      '-1, -1, -1, -1',
      {'dev' : 'WS86008', 'high' : 'RELAY11', 'low' : 'RELAY10'})

buildings['SutardjaDaiHall'].floors['Floor5'].zones['Zone2'] = \
  Zone('Zone 2',
      '-1, -1, -1, -1',
      {'dev' : 'WS86008', 'high' : 'RELAY13', 'low' : 'RELAY12'})
  
buildings['SutardjaDaiHall'].floors['Floor5'].zones['Zone3'] = \
  Zone('Zone 1',
      '-1, -1, -1, -1',
      {'dev' : 'WS86008', 'high' : 'RELAY06', 'low' : 'RELAY07'})

buildings['SutardjaDaiHall'].floors['Floor5'].zones['Zone4'] = \
  Zone('Zone 4',
      '-1, -1, -1, -1',
      {'dev' : 'WS86008', 'high' : 'RELAY08', 'low' : 'RELAY09'})

buildings['SutardjaDaiHall'].floors['Floor5'].zones['Zone5'] = \
  Zone('Zone 5',
      '-1, -1, -1, -1',
      {'dev' : 'WS86008', 'high' : 'RELAY04', 'low' : 'RELAY05'})

buildings['SutardjaDaiHall'].floors['Floor5'].zones['Zone6'] = \
  Zone('Zone 6',
      '-1, -1, -1, -1',
      {'dev' : 'WS86008', 'high' : 'RELAY02', 'low' : 'RELAY03'})

# 6th Floor

buildings['SutardjaDaiHall'].floors['Floor6'].zones['Zone1'] = \
  Zone('Zone 1',
       '60, 100, 295, 160', 
       {'dev' : 'WS86010', 'high' : 'RELAY02', 'low' : 'RELAY03'})

# 7th Floor
buildings['SutardjaDaiHall'].floors['Floor7'].zones['Zone1'] = \
  Zone('Zone 1',
       '10, 117, 79, 229', 
       {'dev' : 'WS86011', 'high' : 'RELAY08', 'low' : 'RELAY09'})

buildings['SutardjaDaiHall'].floors['Floor7'].zones['Zone2'] = \
  Zone('Zone 2',
       '78, 117, 189, 229', 
       {'dev' : 'WS86011', 'high' : 'RELAY10', 'low' : 'RELAY11'})

buildings['SutardjaDaiHall'].floors['Floor7'].zones['Zone3'] = \
  Zone('Zone 3',
       '286, 117, 575, 229', 
       {'dev' : 'WS86011', 'high' : 'RELAY04', 'low' : 'RELAY05'})

buildings['SutardjaDaiHall'].floors['Floor7'].zones['Zone4'] = \
  Zone('Zone 4',
       '575, 117, 657, 230', 
       {'dev' : 'WS86011', 'high' : 'RELAY06', 'low' : 'RELAY07'})

# 6th Floor Demo
#buildings['SutardjaDaiHall'].floors['Floor6'].zones['Zone1'] = \
#  Zone('Zone 1',
#       '60, 100, 295, 160', 
#       {'dev' : 'WS86010', 'high' : 'RELAY01', 'low' : 'RELAY01'})

