import pandas as pd
import numpy as np

"""
I don't really know what this is going to do yet.

Ideas:
    // a search engine, to take any specific criteria and return a list of cars that meet the criteria
    // a model to compare any two cars, with some kind of notion of what makes a car better than another car
        # Maybe this could include comparing a given car to an ideal car of the same field
    // a model that takes a car's stats as input, and ranks the car relative to other cars in it's field
    // a model that can take a car and a target class/type as input, and return a list of target stats which the car
       should meet in order to be competitive 
"""

verbose = False


class FieldRange():
    def __init__(self, bottom, top):

        if isinstance(bottom,str):
            self.bottom = self.mapClassToPI(bottom)
        else:
            self.bottom = bottom
        if isinstance(top,str):
            self.top = self.mapClassToPI(top)
        else:
            self.top = top

        if isinstance(self.bottom,float) and isinstance(self.top,float):
            if self.top < self.bottom:
                temp = self.bottom
                self.bottom = self.top
                self.top = temp



    @staticmethod
    def mapClassToPI(i):
        if i == 'D': return 500
        elif i == 'C': return 600
        elif i == 'B': return 700
        elif i == 'A': return 800
        elif i == 'S1': return 900
        elif i == 'S2': return 998
        elif i == 'X': return 999
        else: return i

class SearchEngine():
    def __init__(self, data, filters=None):

        self.filters = {'car value':'any',
                        'class':'any',
                        'PI':'any',
                        'speed':'any',
                        'handling':'any',
                        'acceleration':'any',
                        'launch':'any',
                        'braking':'any',
                        'offroad':'any',
                        'horsepower':'any',
                        'torque':'any',
                        'weight':'any',
                        'power to weight':'any',
                        '0-60':'any',
                        '60-100':'any',
                        '0-100':'any',
                        '1/4 mile':'any',
                        'top speed':'any',
                        '60-0 distance':'any',
                        '100-0 distance':'any',
                        '60mph gforce':'any',
                        '100mph gforce':'any'}
        self.data = data
        self.entries = None
        self.reqfilters = filters

        self.processFilters()
        self.processSearch()

    def processFilters(self):

        if self.reqfilters is None:
            self.reqfilters = self.filters
            return

        requestedFilteredFields = self.reqfilters.keys()
        for key in requestedFilteredFields:
            self.filters[key] = self.parseField(key, self.reqfilters[key])
            if self.filters[key] != 'any' and verbose:
                minval = str(self.filters[key].bottom)
                maxval = str(self.filters[key].top)
                print('Requested filter: ' + key + ' - understood as: ' +
                      'cars from ' + minval + ' to ' + maxval)
            if self.filters['class'] != 'any' and self.filters['PI'] != 'any':
                self.filters['class'] = 'any'
            elif self.filters['class'] != 'any' and self.filters['PI'] == 'any':
                self.filters['PI'] = self.filters['class']

    def processSearch(self):

        for filt in self.filters.keys():
            if self.filters[filt] != 'any':
                if self.entries is None:
                    if filt == 'car type':
                        self.entries = self.data[self.filters[filt] == self.data[filt]]
                        continue
                    self.entries = self.data[(self.filters[filt].bottom < self.data[filt]) &
                                             (self.filters[filt].top >= self.data[filt])]
                else:
                    if filt == 'car type':
                        self.entries = self.entries[self.filters[filt] == self.entries[filt]]
                        continue
                    self.entries = self.entries[(self.filters[filt].bottom < self.entries[filt]) &
                                                (self.filters[filt].top >= self.entries[filt])]

    @staticmethod
    def parseField(key, field):
        if field == 'any' or key == 'car type':
            return field

        # split comma delimited string
        dashindex = -1
        for c, v in enumerate(field):
            if v == '-':
                dashindex = c
                break

        if dashindex == -1:
            if verbose: print('Filter \'' + key + '\' wants a dash delimited range with no spaces, please.')
            return 'any'
        try:
            return FieldRange(float(field[:dashindex]), float(field[dashindex+1:]))
        except:
            print('Filter \'' + key + '\' input could not be converted to floating point numbers.' +
                  ' Check input type, please.')
            return 'any'


# data from https://www.manteomax.com/
df = pd.read_csv('data.csv')
# remove non FH5 cars
fh5_cars = df.loc[df['Latest game'] == 'FH5']

testfilters = {'PI':'700-400',
               'car type':'Rally Monsters'}

test = SearchEngine(fh5_cars, testfilters)

# currently just prints the names of cars that meet criteria specified in testfilters dict
print(test.entries['name'].tolist())
