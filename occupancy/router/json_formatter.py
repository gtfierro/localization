import json

class Formatter(object):
    """
    Class for dealing with geo.py's data and formatting into JSON
    To be stored in an external file
    """

    def __init__(self, filename, width, height, zones):
        """
        [filename]: of form "filename.json" is the string corresponding
                    to the name of the file we're storing the json in
        [zones]: list of ( (x,y), (x,y), (x,y), (x,y) ) tuples, indicating the
                 UL, UR, LR, LL corners of each zone (clockwise from top left)
        """

        self.width = width
        self.height = height
        self.filename = filename
        for zone in zones:
            if len(zone) != 4:
                raise ValueError('Each zone must have 4 coordinates')
            ul, ur, lr, ll = zone
            if not (ul[0] <= ur[0] and ul[1] == ul[1] and \
                    ur[0] == lr[0] and ur[1] >= lr[1] and \
                    lr[0] >= ll[0] and lr[1] == ll[1] and \
                    ll[0] == ul[0] and ll[1] <= ul[1]):
                raise ValueError('Coordinates must be specified clockwise from the upper left corner \
                    and represent a rectangle')

        self.zones = zones
        self.data = {}

    def update(self, data):
        """
        receives a dict [data] mapping device ip addresses to their coordinates
        """
        if not data: return
        self.data = data

    def to_json(self):
        to_write = {}
        zone_list = []
        for zone in self.zones:
            zone_list.append(list(zone))
        to_write['zones'] = zone_list
        to_write['data']  = self.data
        to_write['width'] = self.width
        to_write['height'] = self.height
        with open(self.filename, mode='w') as f:
            json.dump(to_write,f)

        
