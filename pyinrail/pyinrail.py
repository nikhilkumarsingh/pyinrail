import os
import json
import time
from io import BytesIO
import requests
import demjson
import pytesseract
import pandas as pd
from PIL import Image
from fuzzywuzzy import process

from .utils import *


class RailwayEnquiry:
    """
    The railway enquiry class which has methods to fetch various enquiry details
    """

    def __init__(self, src=None, dest=None, date=None):
        """
        default values of src, dest, date will be used in queries (if they are not passed explicitly)
        """
        self.session = {}
        
        if not os.path.exists(os.path.join(os.path.dirname(__file__), 'stations.json')):
            self.load_stations()
        self.stations = json.load(open(os.path.join(os.path.dirname(__file__), 'stations.json')))
        
        if not os.path.exists(os.path.join(os.path.dirname(__file__), 'trains.json')):
            self.load_trains()
        self.trains = json.load(open(os.path.join(os.path.dirname(__file__), 'trains.json')))
        
        self.src = self.get_stn_code(src) if src else None
        self.dest = self.get_stn_code(dest) if dest else None
        self.date = date
        
        self.create_session()
      
    
    def get_config(self):
        """
        get current configuration of source station, destination station and date of journey
        """
        return {"src": self.src, "dest": self.dest, "date": self.date}


    def check_config(self, src=True, dest=True, date=True):
        """
        check if source, destination and date are prefilled if they are not passed as parameters to some functions
        """
        status = True
        if (src and not self.src) or (dest and not self.dest) or (date and not self.date):
            return False
        else:
            return True
    
    
    def get_quota_choices(self):
        """
        get available quota choices and their codes
        """
        global quotas
        return quotas
    
    
    def load_stations(self):
        """
        fetch and save list of available stations
        """
        timestamp = int(time.time() * 1000)
        url = "http://www.indianrail.gov.in/enquiry/FetchAutoComplete?_={}".format(timestamp)
        r = requests.get(url)
        data = {}
        for station in r.json():
            key = station.split(' - ')[1]
            data[key] = station
        with open(os.path.join(os.path.dirname(__file__), 'stations.json'), "w") as f:
            f.write(json.dumps(data))
   

    def load_trains(self):
        """
        fetch and save list of available trains
        """
        timestamp = int(time.time() * 1000)
        url = "http://www.indianrail.gov.in/enquiry/FetchTrainData?_={}".format(timestamp)
        r = requests.get(url)
        data = {}
        for train in r.json():
            key = train.split(' - ')[0]
            data[key] = train
        with open(os.path.join(os.path.dirname(__file__), 'trains.json'), "w") as f:
            f.write(json.dumps(data))
            
            
    def create_session(self):
        """
        create a session by solving captcha challenge
        """
        self.session['timestamp'] = int(time.time() * 1000)
        url = "http://www.indianrail.gov.in/enquiry/captchaDraw.png?{}".format(self.session['timestamp'])
        r = requests.get(url)
        self.session['cookies'] = r.cookies
        try:
            f = BytesIO(r.content)
        except OSError:
            return None
        im = Image.open(f)
        text = pytesseract.image_to_string(im, lang = 'eng')
        try:
            self.session['captcha'] = eval(text.split("=")[0])
        except:
            self.create_session()
            

    def search_station(self, query):
        """
        search station by name or code
        """
        return [x[0] for x in process.extract(query, self.stations)]
    
    
    def search_train(self, query):
        """
        search train by name or number
        """
        return [x[0] for x in process.extract(query, self.trains.values())]
    
    
    def get_stn_code(self, query):
        """
        utility function to get correst station code
        """
        try:
            return self.stations[query.upper()]
        except KeyError:
            return process.extractOne(query, self.stations.values())[0]
        
    
    def get_trains_between_stations(self, src=None, dest=None, date=None, as_df=False):
        """
        get trains between source and destination stations running on given date

        pass as_df=True to get pandas DataFrame as output
        uses default value of src, dest and date (if not passed)
        """
        src = self.get_stn_code(src)  if src else self.src
        dest = self.get_stn_code(dest) if dest else self.dest
        date = date if date else self.date

        if not all([src,dest,date]) and not self.check_config():
            return "Source, destination or date is empty!"

        params = {
            "inputCaptcha": self.session['captcha'],
            "dt": date,
            "sourceStation": src,
            "destinationStation": dest,
            "language": "en",
            "inputPage": "TBIS",
            "flexiWithDate": "y",
            "_": self.session['timestamp']
        }
        r = requests.get(API_ENDPOINT, params=params, cookies=self.session['cookies'])
        try:
            data = r.json()['trainBtwnStnsList']
        except:
            if r.json()['errorMessage'] == "Session out or Bot attack":
                self.create_session()
                return self.get_trains_between_stations(src, dest, date)
            else:
                return r.json()['errorMessage']
            
        if as_df:
            headers = ['trainName', 'trainNumber', 'fromStnCode', 'toStnCode', 'departureTime', 'arrivalTime',  
                       'duration', 'distance', 'runningMon', 'runningTue', 'runningWed', 'runningThu', 'runningFri', 
                       'runningSat', 'runningSun',  'avlClasses', 'trainType']
            df = pd.DataFrame(data, columns=headers)
            return df
        else:
            return data
        
        
    def get_seat_availability(self, train_no, classc='SL', quota='GN', src=None, 
                              dest=None, date=None, as_df=False):
        """
        get seat availability in a train

        pass as_df=True to get pandas DataFrame as output
        uses default value of src, dest and date (if not passed)
        """
        train_no_code = self.trains[str(train_no)]
        src = self.get_stn_code(src) if src else self.src
        dest = self.get_stn_code(dest) if dest else self.dest
        date = date if date else self.date

        if not all([src,dest,date]) and not self.check_config():
            return "Source, destination or date is empty!"
        
        params = {
            "inputCaptcha": self.session['captcha'],
            "trainNo": train_no_code,
            "classc": classc,
            "quota": quota,
            "dt": date,
            "sourceStation": src,
            "destinationStation": dest,
            "language": "en",
            "inputPage": "SEAT",
            "_": self.session['timestamp']
        }
        r = requests.get(API_ENDPOINT, params=params, cookies=self.session['cookies'])
        try:
            data = r.json()['avlDayList']
        except:
            if r.json()['errorMessage'] == "Session out or Bot attack":
                self.create_session()
                return self.get_seat_availability(train_no, classc=classc, quota=quota, 
                                                  src=src, dest=dest, date=date)
            else:
                return r.json()['errorMessage']
            
        if as_df:
            headers = ['availablityDate', 'availablityStatus', 'availablityType', 'currentBkgFlag', 'reason', 
                       'reasonType', 'waitListType']
            df = pd.DataFrame(data, columns=headers)
            return df
        else:
            return data
    
    
    def get_train_schedule(self, train_no, src=None, date=None, as_df=True):
        """
        get train schedule from a given source station on a given date

        pass as_df=True to get pandas DataFrame as output
        uses default value of src and date (if not passed)
        """
        src = self.get_stn_code(src) if src else self.src
        date = date if date else self.date

        if not all([src,date]) and not self.check_config(dest=False):
            return "Source or date is empty!"
        
        params = {
            "inputCaptcha": self.session['captcha'],
            "trainNo": train_no,
            "journeyDate": date,
            "sourceStation": src,
            "language": "en",
            "inputPage": "TBIS_SCHEDULE_CALL",
            "_": self.session['timestamp']
        }
        r = requests.get(API_ENDPOINT, params=params, cookies=self.session['cookies'])
        try:
            data = r.json()['stationList']
        except:
            if r.json()['errorMessage'] == "Session out or Bot attack":
                self.create_session()
                return self.get_train_schedule(train_no, src=src,date=date)
            else:
                return r.json()['errorMessage']
            
        if as_df:
            headers = ['stationCode', 'stationName', 'departureTime', 'arrivalTime', 'routeNumber', 'haltTime', 
                       'distance', 'dayCount', 'stnSerialNumber']
            df = pd.DataFrame(data, columns=headers)
            return df
        else:
            return data
        

    def get_train_fare(self, train_no, classc='SL', quota='GN', src=None, dest=None, date=None):
        """
        get train fare details b/w two stations on a given date

        uses default value of src, dest and date (if not passed)
        """
        train_no_code = self.trains[str(train_no)]
        src = self.get_stn_code(src) if src else self.src
        dest = self.get_stn_code(dest) if dest else self.dest
        date = date if date else self.date

        if not all([src,dest,date]) and not self.check_config():
            return "Source, destination or date is empty!"
        
        columns = ['baseFare', 'reservationCharge', 'superfastCharge', 'fuelAmount', 'totalConcession', 
                   'tatkalFare', 'goodsServiceTax', 'otherCharge', 'cateringCharge', 'dynamicFare', 'totalFare', 
                   'wpServiceCharge', 'wpServiceTax', 'travelInsuranceCharge', 'travelInsuranceServiceTax', 
                   'totalCollectibleAmount']
        
        params = {
            "inputCaptcha": self.session['captcha'],
            "trainNo": train_no_code,
            "classc": classc,
            "quota": quota,
            "dt": date,
            "sourceStation": src,
            "destinationStation": dest,
            "language": "en",
            "inputPage": "FARE",
            "_": self.session['timestamp']
        }
        r = requests.get(API_ENDPOINT, params=params, cookies=self.session['cookies'])
        try:
            data = {}
            for key,val in r.json().items():
                if key in columns:
                    data[key] = r.json()[key]
            return data
        except:
            if r.json()['errorMessage'] == "Session out or Bot attack":
                self.create_session()
                return self.get_seat_availability(train_no, classc=classc, quota=quota, 
                    src=src, dest=dest, date=date)
            else:
                return r.json()['errorMessage']
            
            
    def get_pnr_status(self, pnr_no):
        """
        get pnr status 
        """
        params = {
            "inputCaptcha": self.session['captcha'],
            "inputPnrNo": pnr_no,
            "language": "en",
            "inputPage": "PNR",
            "_": self.session['timestamp']
        }
        r = requests.get(API_ENDPOINT, params=params, cookies=self.session['cookies'])
        try:
            return r.json()
        except:
            if r.json()['errorMessage'] == "Session out or Bot attack":
                self.create_session()
                return self.get_pnr_status(pnr_no)
            else:
                return r.json()['errorMessage']
            
    
    def get_train_status(self, train_no, as_df=False):
        """
        get live train running status

        pass as_df=True to get pandas DataFrames as output
        """
        # cookie generator
        url = "https://enquiry.indianrail.gov.in/ntes/SearchTrain?trainNo={}".format(train_no)
        r = requests.get(url)

        url = "https://enquiry.indianrail.gov.in/ntes/NTES?action=getTrainData&trainNo={}".format(train_no)
        r = requests.get(url, cookies=r.cookies)

        data = {}
        parts = r.text.replace('\n','').replace('\t','').replace("\"", "").split(',')
        for part in parts[1:9]:
            key, val = part.split(':',1)
            data[key] = val

        data['rakes'] = demjson.decode(r.text.split('rakes:')[1].split(']}')[0]+']')
        
        if as_df:
            general_columns = ['startDate', 'departed', 'curStn', 'terminated', 'lastUpdated', 'totalLateMins']
            station_columns = ['stnCode', 'arr', 'schArrTime', 'actArr', 'delayArr', 'dep', 'schDepTime', 
                               'actDep', 'delayDep', 'dayCnt', 'schDayCnt', 'distance']
            rakes_df = pd.DataFrame(data['rakes'], columns=general_columns)
            rakes_data = []
            for rake in data['rakes']:
                rakes_data.append(pd.DataFrame(rake['stations'], columns=station_columns))
            train_data = data
            train_data.pop('rakes')
            return train_data, rakes_df, rakes_data
        else:
            return data


    def find_available(self, src=None, dest=None, date=None):
        """
        a utility to print trains and their classes in which seats are AVAILABLE 

        uses default value of src, dest and date (if not passed)
        """
        src = self.get_stn_code(src)  if src else self.src
        dest = self.get_stn_code(dest) if dest else self.dest
        date = date if date else self.date
        
        df = self.get_trains_between_stations(src=src, dest=dest, date=date, as_df=True)
        for x in range(len(df)):
            train = df.loc[x]
            print(train['trainName'], train['departureTime'], '-', train['arrivalTime'])
            for c in train['avlClasses']:
                train_params = {'src': train['fromStnCode'], 'dest': train['toStnCode'], 'date': date, 'classc': c}
                status_df = self.get_seat_availability(train['trainNumber'], **train_params, as_df=True)
                status_df = status_df[status_df['availablityStatus'].str.contains('AVAILABLE-')]
                if len(status_df):
                    print(c, self.get_train_fare(train['trainNumber'], **train_params)['totalFare'])
                    display(status_df)