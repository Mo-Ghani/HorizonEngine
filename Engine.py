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

verbose = True
#pd.set_option('display.max_columns', None)

class FieldRange():
    def __init__(self, bottom, top=None):

        if top is None:
            self.bottom = self.mapClassToPI(bottom) - 100
            if self.bottom != 998:
                self.top = self.bottom + 100
            else:
                self.top = 999
        else:
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
    def __init__(self, data, filters=None, reqsearchmode=None):

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

        self.rankableFeatures = ['PI','speed','handling','acceleration','launch',
                                 'braking','offroad','horsepower','torque','weight','0-60',
                                 '60-100','0-100','1/4 mile','top speed','60-0 distance',
                                 '100-0 distance','60mph gforce','100mph gforce']

        self.searchModes = {'car value': 'all',
                            'class': 'all',
                            'PI': 'all',
                            'speed': 'all',
                            'handling': 'all',
                            'acceleration': 'all',
                            'launch': 'all',
                            'braking': 'all',
                            'offroad': 'all',
                            'horsepower': 'all',
                            'torque': 'all',
                            'weight': 'all',
                            'power to weight': 'all',
                            '0-60': 'all',
                            '60-100': 'all',
                            '0-100': 'all',
                            '1/4 mile': 'all',
                            'top speed': 'all',
                            '60-0 distance': 'all',
                            '100-0 distance': 'all',
                            '60mph gforce': 'all',
                            '100mph gforce': 'all'}

        self.data = data
        self.entries = None
        self.reqfilters = filters
        self.reqsearchmode = reqsearchmode
        self.rankedCars = []

        self.processSearchMode()
        self.processFilters()
        self.processSearch()

    def processSearchMode(self):
        if self.reqsearchmode is None:
            return

        requestedSearchFields = self.reqsearchmode.keys()
        for key in requestedSearchFields:
            self.searchModes[key] = self.parseField(key, self.reqfilters[key])
            if self.filters[key] != 'any' and verbose:
                minval = str(self.filters[key].bottom)
                maxval = str(self.filters[key].top)
                print('Requested filter: ' + key + ' - understood as: ' +
                      'cars from ' + minval + ' to ' + maxval)
            if self.filters['class'] != 'any' and self.filters['PI'] != 'any':
                self.filters['class'] = 'any'
            elif self.filters['class'] != 'any' and self.filters['PI'] == 'any':
                self.filters['PI'] = self.filters['class']

    def processFilters(self):

        if self.reqfilters is None:
            return

        requestedFilteredFields = self.reqfilters.keys()
        for key in requestedFilteredFields:
            self.filters[key] = self.parseField(key, self.reqfilters[key], 1)
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

        changed = False
        for filt in self.filters.keys():
            if filt == 'class':
                continue
            if self.filters[filt] != 'any':
                changed = True
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
                    self.entries = self.entries[(self.filters[filt].bottom < float(self.entries[filt])) &
                                                (self.filters[filt].top >= float(self.entries[filt]))]
        if not changed:
            self.entries = self.data

    def rankByPoints(self):

        if len(self.entries) == 0:
            self.rankedCars = None
            return

        self.entries = self.entries.reset_index(drop=True)
        totalScores = np.array([[0, i] for i in range(len(self.entries))])

        for field in self.rankableFeatures:
            ascending = False
            if field in ['weight', 'car value']:
                ascending = True
            self.entries = self.entries.sort_values([field], ascending=ascending)
            for i in range(len(self.entries)):
                totalScores[self.entries.index[i]][0] += len(self.entries) - i

        ranked = totalScores[totalScores[:, 0].argsort()][::-1]

        self.rankedCars = ranked

    def printRanked(self):

        if self.rankedCars is None:
            print("No Cars passed your cuts.")
            return

        for c in range(len(self.rankedCars)):
            print("Position " + str(c+1) + " with " + str(self.rankedCars[c][0]) + " points: " + str(self.entries.loc[
                self.rankedCars[c][1]]["name"]))

    @staticmethod
    def parseField(key, field, mode):
        if mode == 0:
            pass

        else:
            if field == 'any' or key == 'car type':
                return field

            # split comma delimited string
            dashindex = -1
            for c, v in enumerate(field):
                if v == '-':
                    dashindex = c
                    break

            if key == 'class':
                if dashindex == -1:
                    return FieldRange(field)
                else:
                    return FieldRange(field[:dashindex], field[dashindex+1:])

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

testfilters = {'0-60':'0-1'}

test = SearchEngine(fh5_cars, testfilters)

# currently just prints the names of cars that meet criteria specified in testfilters dict
test.rankByPoints()
test.printRanked()

