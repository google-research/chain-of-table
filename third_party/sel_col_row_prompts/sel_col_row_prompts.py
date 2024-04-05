# MIT License
# 
# Copyright (c) 2022 Alibaba Research
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.


select_column_demo = """Use f_col() api to filter out useless columns in the table according to informations in the statement and the table.

/*
{
  "table_caption": "south wales derby",
  "columns": ["competition", "total matches", "cardiff win", "draw", "swansea win"],
  "table_column_priority": [
    ["competition", "league", "fa cup", "league cup"],
    ["total matches", "55", "2", "5"],
    ["cardiff win", "19", "0", "2"],
    ["draw", "16", "27", "0"],
    ["swansea win", "20", "2", "3"]
  ]
}
*/
statement : there are no cardiff wins that have a draw greater than 27.
similar words link to columns :
no cardiff wins -> cardiff win
a draw -> draw
column value link to columns :
27 -> draw
semantic sentence link to columns :
None
The answer is : f_col([cardiff win, draw])

/*
{
  "table_caption": "gambrinus liga",
  "columns": ["season", "champions", "runner - up", "third place", "top goalscorer", "club"],
  "table_column_priority": [
    ["season", "1993 - 94", "1994 - 95", "1995 - 96"],
    ["champions", "sparta prague (1)", "sparta prague (2)", "slavia prague (1)"],
    ["runner - up", "slavia prague", "slavia prague", "sigma olomouc"],
    ["third place", "ban\u00edk ostrava", "fc brno", "baumit jablonec"],
    ["top goalscorer", "horst siegl (20)", "radek drulák (15)", "radek drulák (22)"],
    ["club", "sparta prague", "drnovice", "drnovice"]
  ]
}
*/
statement : the top goal scorer for the season 2010 - 2011 was david lafata.
similar words link to columns :
season 2010 - 2011 -> season
the top goal scorer -> top goalscorer
column value link to columns :
2010 - 2011 -> season
semantic sentence link to columns :
the top goal scorer for ... was david lafata -> top goalscorer
The answer is : f_col([season, top goalscorer])

/*
{
  "table_caption": "head of the river (queensland)",
  "columns": ["crew", "open 1st viii", "senior 2nd viii", "senior 3rd viii", "senior iv", "year 12 single scull", "year 11 single scull"],
  "table_column_priority": [
    ["crew", "2009", "2010", "2011"],
    ["open 1st viii", "stm", "splc", "stm"],
    ["senior 2nd viii", "sta", "som", "stu"],
    ["senior 3rd viii", "sta", "som", "stu"],
    ["senior iv", "som", "sth", "sta"],
    ["year 12 single scull", "stm", "splc", "stm"],
    ["year 11 single scull", "splc", "splc", "splc"]
  ]
}
*/
statement : the crew that had a senior 2nd viii of som and senior iv of stm was that of 2013.
similar words link to columns :
the crew -> crew
a senior 2nd viii of som -> senior 2nd viii
senior iv of stm -> senior iv
column value link to columns :
som -> senior 2nd viii
stm -> senior iv
semantic sentence link to columns :
None
The answer is : f_col([crew, senior 2nd viii, senior iv])

/*
{
  "table_caption": "2007 - 08 boston celtics season",
  "columns": ["game", "date", "team", "score", "high points", "high rebounds", "high assists", "location attendance", "record"],
  "table_column_priority": [
    ["game", "74", "75", "76"],
    ["date", "april 1", "april 2", "april 5"],
    ["team", "chicago", "indiana", "charlotte"],
    ["score", "106 - 92", "92 - 77", "101 - 78"],
    ["high points", "allen (22)", "garnett (20)", "powe (22)"],
    ["high rebounds", "perkins (9)", "garnett (11)", "powe (9)"],
    ["high assists", "rondo (10)", "rondo (6)", "rondo (5)"],
    ["location attendance", "united center 22225", "td banknorth garden 18624", "charlotte bobcats arena 19403"],
    ["record", "59 - 15", "60 - 15", "61 - 15"]
  ]
}
*/
statement : in game 74 against chicago , perkins had the most rebounds (9) and allen had the most points (22).
similar words link to columns :
the most rebounds -> high rebounds
the most points -> high points
in game 74 -> game
column value link to columns :
74 -> game
semantic sentence link to columns :
2007 - 08 boston celtics season in game 74 against chicago -> team
perkins had the most rebounds -> high rebounds
allen had the most points -> high points
The answer is : f_col([game, team, high points, high rebounds])

/*
{
  "table_caption": "dan hardy",
  "columns": ["res", "record", "opponent", "method", "event", "round", "time", "location"],
  "table_column_priority": [
    ["res", "win", "win", "loss"],
    ["record", "25 - 10 (1)", "24 - 10 (1)", "23 - 10 (1)"],
    ["opponent", "amir sadollah", "duane ludwig", "chris lytle"],
    ["method", "decision (unanimous)", "ko (punch and elbows)", "submission (guillotine choke)"],
    ["event", "ufc on fuel tv : struve vs miocic", "ufc 146", "ufc live : hardy vs lytle"],
    ["round", "3", "1", "5"],
    ["time", "5:00", "3:51", "4:16"],
    ["location", "nottingham , england", "las vegas , nevada , united states", "milwaukee , wisconsin , united states"]
  ]
}
*/
statement : the record of the match was a 10 - 3 (1) score , resulting in a win in round 5 with a time of 5:00 minutes.
similar words link to columns :
the record of the match was a 10 - 3 (1) score -> record
the record -> record
in round -> round
a time -> time
column value link to columns :
10 - 3 (1) -> record
5 -> round
5:00 minutes -> time
semantic sentence link to columns :
resulting in a win -> res
The answer is : f_col([res, record, round, time])

/*
{
  "table_caption": "list of largest airlines in central america & the caribbean",
  "columns": ["rank", "airline", "country", "fleet size", "remarks"],
  "table_column_priority": [
    ["rank", "1", "2", "3"],
    ["airline", "caribbean airlines", "liat", "cubana de aviaci\u00e3 cubicn"],
    ["country", "trinidad and tobago", "antigua and barbuda", "cuba"],
    ["fleet size", "22", "17", "14"],
    ["remarks", "largest airline in the caribbean", "second largest airline in the caribbean", "operational since 1929"]
  ]
}
*/
statement : the remark on airline of dutch antilles express with fleet size over 4 is curacao second national carrier.
similar words link to columns :
the remark -> remarks
on airline -> airline
fleet size -> fleet size
column value link to columns :
dutch antilles -> country
4 -> fleet size
curacao second national carrier -> remarks
semantic sentence link to columns :
None
The answer is : f_col([airline, fleet size, remarks])

/*
{
  "table_caption": "cnbc prime 's the profit 200",
  "columns": ["year", "date", "driver", "team", "manufacturer", "laps", "-", "race time", "average speed (mph)"],
  "table_column_priority": [
    ["year", "1990", "1990", "1991"],
    ["date", "july 15", "october 14", "july 14"],
    ["driver", "tommy ellis", "rick mast", "kenny wallace"],
    ["team", "john jackson", "ag dillard motorsports", "rusty wallace racing"],
    ["manufacturer", "buick", "buick", "pontiac"],
    ["laps", "300", "250", "300"],
    ["-", "317.4 (510.805)", "264.5 (425.671)", "317.4 (510.805)"],
    ["race time", "3:41:58", "2:44:37", "2:54:38"],
    ["average speed (mph)", "85.797", "94.405", "109.093"]
  ]
}
*/
statemnet : on june 26th , 2010 kyle busch drove a total of 211.6 miles at an average speed of 110.673 miles per hour.
similar words link to columns :
drove -> driver
column value link to columns :
june 26th , 2010 -> date, year
a total of 211.6 miles -> -
semantic sentence link to columns :
kyle busch drove -> driver
an average speed of 110.673 miles per hour -> average speed (mph)
The answer is : f_col([year, date, driver, -, average speed (mph)])

/*
{
  "table_caption": "2000 ansett australia cup",
  "columns": ["home team", "home team score", "away team", "away team score", "ground", "crowd", "date"],
  "table_column_priority": [
    ["home team", "brisbane lions", "kangaroos", "richmond"],
    ["home team score", "13.6 (84)", "10.16 (76)", "11.16 (82)"],
    ["away team", "sydney", "richmond", "brisbane lions"],
    ["away team score", "17.10 (112)", "9.11 (65)", "15.9 (99)"],
    ["ground", "bundaberg rum stadium", "waverley park", "north hobart oval"],
    ["crowd", "8818", "16512", "4908"],
    ["date", "friday , 28 january", "friday , 28 january", "saturday , 5 february"]
  ]
}
*/
statement : sydney scored the same amount of points in the first game of the 2000 afl ansett australia cup as their opponent did in their second.
similar words link to columns :
scored -> away team score, home team score
column value link to columns :
sydney -> away team, home team
semantic sentence link to columns :
their opponent -> home team, away team
scored the same amount of points -> away team score, home team score
first game -> date
their second -> date
sydney scored -> home team, away team, home team score, away team score
The answer is : f_col([away team, home team, away team score, home team score, date])"""


select_row_demo = """Using f_row() api to select relevant rows in the given table that support or oppose the statement.
Please use f_row([*]) to select all rows in the table.

/*
table caption : 1972 vfl season.
col : home team | home team score | away team | away team score | venue | crowd | date
row 1 : st kilda | 13.12 (90) | melbourne | 13.11 (89) | moorabbin oval | 18836 | 19 august 1972
row 2 : south melbourne | 9.12 (66) | footscray | 11.13 (79) | lake oval | 9154 | 19 august 1972
row 3 : richmond | 20.17 (137) | fitzroy | 13.22 (100) | mcg | 27651 | 19 august 1972
row 4 : geelong | 17.10 (112) | collingwood | 17.9 (111) | kardinia park | 23108 | 19 august 1972
row 5 : north melbourne | 8.12 (60) | carlton | 23.11 (149) | arden street oval | 11271 | 19 august 1972
row 6 : hawthorn | 15.16 (106) | essendon | 12.15 (87) | vfl park | 36749 | 19 august 1972
*/
statement : the away team with the highest score is fitzroy.
explain : the statement want to check the highest away team score. we need to compare score of away team fitzroy with all others, so we need all rows. use * to represent all rows in the table.
The answer is : f_row([*])

/*
table caption : list of largest airlines in central america & the caribbean.
col : rank | airline | country | fleet size | remarks
row 1 : 1 | caribbean airlines | trinidad and tobago | 22 | largest airline in the caribbean
row 2 : 2 | liat | antigua and barbuda | 17 | second largest airline in the caribbean
row 3 : 3 | cubana de aviaciã cubicn | cuba | 14 | operational since 1929
row 4 : 4 | inselair | curacao | 12 | operational since 2006
row 5 : 5 | dutch antilles express | curacao | 4 | curacao second national carrier
row 6 : 6 | air jamaica | trinidad and tobago | 5 | parent company is caribbean airlines
row 7 : 7 | tiara air | aruba | 3 | aruba 's national airline
*/
statement : the remark on airline of dutch antilles express with fleet size over 4 is curacao second national carrier.
explain : the statement want to check a record in the table. we cannot find a record perfectly satisfied the statement, the most relevant row is row 5, which describes dutch antilles express airline, remarks is uracao second national carrier and fleet size is 4 not over 4.
The answer is : f_row([row 5])

/*
table caption : list of longest - serving soap opera actors.
col : actor | character | soap opera | years | duration
row 1 : tom jordon | charlie kelly | fair city | 1989- | 25 years
row 2 : tony tormey | paul brennan | fair city | 1989- | 25 years
row 3 : jim bartley | bela doyle | fair city | 1989- | 25 years
row 4 : sarah flood | suzanne halpin | fair city | 1989 - 2013 | 24 years
row 5 : pat nolan | barry o'hanlon | fair city | 1989 - 2011 | 22 years
row 6 : martina stanley | dolores molloy | fair city | 1992- | 22 years
row 7 : joan brosnan walsh | mags kelly | fair city | 1989 - 2009 | 20 years
row 8 : jean costello | rita doyle | fair city | 1989 - 2008 , 2010 | 19 years
row 9 : ciara o'callaghan | yvonne gleeson | fair city | 1991 - 2004 , 2008- | 19 years
row 10 : celia murphy | niamh cassidy | fair city | 1995- | 19 years
row 39 : tommy o'neill | john deegan | fair city | 2001- | 13 years
row 40 : seamus moran | mike gleeson | fair city | 1996 - 2008 | 12 years
row 41 : rebecca smith | annette daly | fair city | 1997 - 2009 | 12 years
row 42 : grace barry | mary - ann byrne | glenroe | 1990 - 2001 | 11 years
row 43 : gemma doorly | sarah o'leary | fair city | 2001 - 2011 | 10 years
*/
statement : seamus moran and rebecca smith were in soap operas for a duration of 12 years.
explain : the statement want to check seamus moran and rebecca smith in the table. row 40 describes seamus moran were in soap operas for a duration of 12 years. row 41 describes rebecca smith were in soap operas for a duration of 12 years
The answer is : f_row([row 40, row 41])

/*
table caption : jeep grand cherokee.
col : years | displacement | engine | power | torque
row 1 : 1999 - 2004 | 4.0l (242cid) | power tech i6 | - | 3000 rpm
row 2 : 1999 - 2004 | 4.7l (287cid) | powertech v8 | - | 3200 rpm
row 3 : 2002 - 2004 | 4.7l (287cid) | high output powertech v8 | - | -
row 4 : 1999 - 2001 | 3.1l diesel | 531 ohv diesel i5 | - | -
row 5 : 2002 - 2004 | 2.7l diesel | om647 diesel i5 | - | -
*/
statement : the jeep grand cherokee with the om647 diesel i5 had the third lowest numbered displacement.
explain : the statement want to check the om647 diesel i5 had third lowest numbered displacement. so we need first three low numbered displacement and all rows that power is om647 diesel i5.
The answer is : f_row([row 5, row 4, row 1])"""

