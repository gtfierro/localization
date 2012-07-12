import buildingdata
import bacnet_io
import time

bn = bacnet_io.BacnetIO('db_ws')

def set_light(zone, low_setting, high_setting,retries_left):
    """
    Checks current setting for lights and only writes to lights if the requested
    settings are different
    """
    if retries_left <= 0:
        return

    low_obj = bn.find(zone.controls['low'],zone.controls['dev'])
    high_obj = bn.find(zone.controls['high'],zone.controls['dev'])
    current_setting = low_obj.read_point()
    if current_setting != int(low_setting):
        low_obj.read_point()
        low_obj.write_point(bacnet_io.BACNET_APPLICATION_TAG_ENUMERATED, low_setting)
        low_obj.read_point()
        low_obj.write_point(bacnet_io.BACNET_APPLICATION_TAG_ENUMERATED, low_setting)
        low_obj.read_point()
        low_obj.write_point(bacnet_io.BACNET_APPLICATION_TAG_ENUMERATED, low_setting)
    current_setting = high_obj.read_point()
    if current_setting != int(high_setting):
        high_obj.read_point()
        high_obj.write_point(bacnet_io.BACNET_APPLICATION_TAG_ENUMERATED, high_setting)
        high_obj.read_point()
        high_obj.write_point(bacnet_io.BACNET_APPLICATION_TAG_ENUMERATED, high_setting)
        high_obj.read_point()
        high_obj.write_point(bacnet_io.BACNET_APPLICATION_TAG_ENUMERATED, high_setting)

    #if the writes didn't work, try again
    if get_level(zone) != (low_setting + 2 * high_setting):
        set_light(zone, low_setting, high_setting, retries_left - 1)

def get_level(zone):
  """
  Retrieves the current level of the light. I tested this with combinations of actual wall
  switches and direct manipulation of BACnet, and this returned the correct light level
  each time!
  """
  low_obj = bn.find(zone.controls['low'],zone.controls['dev'])
  high_obj = bn.find(zone.controls['high'],zone.controls['dev'])
  for i in range(2):
      low_obj.read_point(bacnet_io.PROP_PRIORITY_ARRAY) 
      high_obj.read_point(bacnet_io.PROP_PRIORITY_ARRAY)
      low_obj.read_point(bacnet_io.PROP_PRIORITY_ARRAY) 
      high_obj.read_point(bacnet_io.PROP_PRIORITY_ARRAY)
      low_obj.read_point() + 2*high_obj.read_point()

  return low_obj.read_point() + 2*high_obj.read_point()

def get_priority_array(zone):
  low_obj = bn.find(zone.controls['low'],zone.controls['dev'])
  high_obj = bn.find(zone.controls['high'],zone.controls['dev'])
  low_array = low_obj.read_point(bacnet_io.PROP_PRIORITY_ARRAY)
  high_array = high_obj.read_point(bacnet_io.PROP_PRIORITY_ARRAY)
  #return in form (low, high)
  return (low_array,high_array)


def set_level(zone, level):
  if isinstance(zone, str):
    zone = buildingdata.buildings['SutardjaDaiHall'].floors['Floor4'].zones[zone]
  retries = 2
  if level == 0:
    set_light(zone, 0, 0, retries)
  elif level == 1: 
    set_light(zone, 1, 0, retries)
  elif level == 2: 
    set_light(zone, 0, 1, retries)
  elif level == 3: 
    set_light(zone, 1, 1, retries)
  else:
    print "Unknown level", level


