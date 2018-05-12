[![PyPI](https://img.shields.io/badge/PyPi-v1.0.0-f39f37.svg)](https://pypi.python.org/pypi/pyinrail)
[![license](https://img.shields.io/github/license/mashape/apistatus.svg?maxAge=2592000)](https://github.com/nikhilkumarsingh/pyinrail/blob/master/LICENSE.txt)

# pyinrail

A python wrapper for Indian Railways Enquiry API!

- Get trains between stations
- Get seat availability
- Get train fare
- Get train schedule
- Get train live running status
- Get PNR status

...and much more!

## Installation

To install pyinrail, simply,

```
$ pip install pyinrail
```

You will also need to install tesseract-ocr. Find instructions to install tesseract-ocr [here](https://github.com/tesseract-ocr/tesseract/wiki).

## Usage

- Importing pyinrail

```python
from pyinrail import pyinrail
```
- Create **RailwayEnquiry** object
```python
enq = pyinrail.RailwayEnquiry(src='new delhi', dest='ahmedabad', date='12-05-2018')
```

- Get trains between stations

```python
df = enq.get_trains_between_stations(as_df=True)
print(df)
```

```
         trainName trainNumber fromStnCode toStnCode departureTime arrivalTime duration  distance        avlClasses
0  ADI SJ RAJDHANI       12958        NDLS       ADI         19:55       09:40    13:45       935      [1A, 2A, 3A]
1  GUJRAT S KRANTI       12918         NZM       ADI         13:55       06:10    16:15      1085      [2A, 3A, SL]
2   ASHRAM EXPRESS       12916         DLI       ADI         15:20       07:40    16:20       934  [1A, 2A, 3A, SL]
3   ALA HAZRAT EXP       14311         DLI       ADI         11:45       06:15    18:30       933      [2A, 3A, SL]
4     YOGA EXPRESS       19032         DSA       ADI         21:26       17:10    19:44       963  [1A, 2A, 3A, SL]
5  DEE BDTS G RATH       12215         DEE       ADI         09:20       01:10    15:50       951              [3A]
```

- Get seat availability

```python
df = enq.get_seat_availability(12958, classc='2A', as_df=True)
print(df)
```

```
  availablityDate availablityStatus  availablityType currentBkgFlag reason reasonType  waitListType
0       12-5-2018    TRAIN DEPARTED             8224              Y                 W          8224
1       13-5-2018       GNWL68/WL24             8224              N                 S             9
2       14-5-2018        GNWL41/WL8             8224              N                 S             9
3       15-5-2018        GNWL25/WL6             8224              N                 S             9
4       16-5-2018       GNWL33/WL14             8224              N                 S             9
5       17-5-2018        GNWL20/WL9             8224              N                 S             9
```

- Get train schedule

```python
df = enq.get_train_schedule(12958, as_df=True)
print(df)
```

```
   stationCode   stationName departureTime arrivalTime routeNumber haltTime distance dayCount stnSerialNumber
0         NDLS     NEW DELHI         19:55          --           1       --        0        1               1
1          DEC   DELHI CANTT         20:25       20:23           1    02:00       16        1               2
2          GGN       GURGAON         20:43       20:41           1    02:00       32        1               3
3           JP        JAIPUR         00:30       00:20           1    10:00      309        2               4
4          AII      AJMER JN         02:29       02:25           1    04:00      443        2               5
5           FA         FALNA         04:53       04:52           1    01:00      650        2               6
6          ABR      ABU ROAD         06:05       06:01           1    04:00      748        2               7
7          PNU   PALANPUR JN         07:12       07:10           1    02:00      801        2               8
8          MSH   MAHESANA JN         08:05       08:03           1    02:00      866        2               9
9         SBIB  SABARMATI BG         09:02       09:00           1    02:00      929        2              10
10         ADI  AHMEDABAD JN            --       09:40           1       --      935        2              11
```

- Get train fare

```python
fare_data = enq.get_train_fare(12958, classc='2A')
print(fare_data)
```

```
{'baseFare': 1841,
 'cateringCharge': 225,
 'dynamicFare': 921,
 'fuelAmount': 0.0,
 'goodsServiceTax': 143.0,
 'otherCharge': 0,
 'reservationCharge': 50,
 'superfastCharge': 45,
 'tatkalFare': 0,
 'totalCollectibleAmount': 3225.0,
 'totalConcession': 0,
 'totalFare': 3225,
 'travelInsuranceCharge': 0.0,
 'travelInsuranceServiceTax': 0.0,
 'wpServiceCharge': 0.0,
 'wpServiceTax': 0.0}
```

- Get train's live running status

```python
train_detail, instances, detailed_instances = enq.get_train_status(12958, as_df=True)
print(train_detail)
print(instances)
print(detailed_instances[0])
```

```
{'dayCnt': '1',
 'from': 'NDLS',
 'runsOn': '1111111',
 'schArrTime': '09:40',
 'schDepTime': '19:55',
 'to': 'ADI',
 'trainName': 'ADI SJ RAJDHANI',
 'trainNo': '12958'}


     startDate  departed curStn  terminated        lastUpdated  totalLateMins
0  12 May 2018      True     RE       False  12 May 2018 21:43              6
1  11 May 2018      True    ADI        True   12 May 2018 9:27            -14


   stnCode    arr schArrTime actArr  delayArr    dep schDepTime actDep  delayDep  dayCnt  schDayCnt  distance
0     NDLS  False      00:00  00:00         0   True      19:55  19:55         0       0          0         0
1      DEC   True      20:23  20:27         4   True      20:25  20:29         4       0          0        15
2      GGN   True      20:41  20:47         6   True      20:43  20:49         6       0          0        32
3       RE   True      21:30  21:41        11   True      21:30  21:41        11       0          0        83
4       JP  False      00:20  00:20         0  False      00:30  00:30         0       1          1       308
5      AII  False      02:25  02:25         0  False      02:29  02:29         0       1          1       442
6       FA  False      04:52  04:52         0  False      04:53  04:53         0       1          1       649
7      ABR  False      06:01  06:01         0  False      06:05  06:05         0       1          1       747
8      PNU  False      07:10  07:10         0  False      07:12  07:12         0       1          1       800
9      MSH  False      08:03  08:03         0  False      08:05  08:05         0       1          1       865
10    SBIB  False      09:00  09:00         0  False      09:02  09:02         0       1          1       927
11     ADI  False      09:40  09:40         0  False      00:00  00:00         0       1          1       934
```

## TODOs

- [ ] A command line client
- [ ] A GUI interface


## Want to contribute?

- Clone the repository

	```
	$ git clone http://github.com/nikhilkumarsingh/pyinrail
	```

- Install dependencies
	
	```
	$ pip install -r requirements.txt
	```

- To test local version of pyinrail:
	```
	$ pip install -U .
	```
	OR :
	```
	$ pip install -e <project dir.> .
	```
