import json
import copy
import re
import numpy as np
from utils.helper import table2df, NoIndent, MyEncoder


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


def twoD_list_transpose(arr, keep_num_rows=3):
    arr = arr[: keep_num_rows + 1] if keep_num_rows + 1 <= len(arr) else arr
    return [[arr[i][j] for i in range(len(arr))] for j in range(len(arr[0]))]


def select_column_build_prompt(table_text, statement, table_caption=None, num_rows=100):
    df = table2df(table_text, num_rows=num_rows)
    tmp = df.values.tolist()
    list_table = [list(df.columns)] + tmp
    list_table = twoD_list_transpose(list_table, len(list_table))
    if table_caption is not None:
        dic = {
            "table_caption": table_caption,
            "columns": NoIndent(list(df.columns)),
            "table_column_priority": [NoIndent(i) for i in list_table],
        }
    else:
        dic = {
            "columns": NoIndent(list(df.columns)),
            "table_column_priority": [NoIndent(i) for i in list_table],
        }
    linear_dic = json.dumps(
        dic, cls=MyEncoder, ensure_ascii=False, sort_keys=False, indent=2
    )
    prompt = "/*\ntable = " + linear_dic + "\n*/\n"
    prompt += "statement : " + statement + ".\n"
    prompt += "similar words link to columns :\n"
    return prompt


def select_column_func(sample, table_info, llm, llm_options, debug=False, num_rows=100):
    # table_info = get_table_info(sample)
    table_text = table_info["table_text"]

    table_caption = sample["table_caption"]
    statement = sample["statement"]

    prompt = "" + select_column_demo.rstrip() + "\n\n"
    prompt += select_column_build_prompt(
        table_text, statement, table_caption, num_rows=num_rows
    )

    responses = llm.generate_plus_with_score(prompt, options=llm_options)

    if debug:
        print(prompt)
        print(responses)

    pattern_col = r"f_col\(\[(.*?)\]\)"

    pred_conf_dict = {}
    for res, score in responses:
        try:
            pred = re.findall(pattern_col, res, re.S)[0].strip()
        except Exception:
            continue
        pred = pred.split(", ")
        pred = [i.strip() for i in pred]
        pred = sorted(pred)
        pred = str(pred)
        if pred not in pred_conf_dict:
            pred_conf_dict[pred] = 0
        pred_conf_dict[pred] += np.exp(score)

    select_col_rank = sorted(pred_conf_dict.items(), key=lambda x: x[1], reverse=True)

    operation = {
        "operation_name": "select_column",
        "parameter_and_conf": select_col_rank,
    }

    sample_copy = copy.deepcopy(sample)
    sample_copy["chain"].append(operation)

    return sample_copy


def select_column_act(table_info, operation, union_num=2, skip_op=[]):
    table_info = copy.deepcopy(table_info)

    failure_table_info = copy.deepcopy(table_info)
    failure_table_info["act_chain"].append("skip f_select_column()")

    if "select_column" in skip_op:
        return failure_table_info

    def union_lists(to_union):
        return list(set().union(*to_union))

    def twoD_list_transpose(arr):
        return [[arr[i][j] for i in range(len(arr))] for j in range(len(arr[0]))]

    selected_columns_info = operation["parameter_and_conf"]
    selected_columns_info = sorted(
        selected_columns_info, key=lambda x: x[1], reverse=True
    )
    selected_columns_info = selected_columns_info[:union_num]
    selected_columns = [x[0] for x in selected_columns_info]
    selected_columns = [eval(x) for x in selected_columns]
    selected_columns = union_lists(selected_columns)

    real_selected_columns = []

    table_text = table_info["table_text"]
    table = twoD_list_transpose(table_text)
    new_table = []
    for cols in table:
        if cols[0].lower() in selected_columns:
            real_selected_columns.append(cols[0])
            new_table.append(copy.deepcopy(cols))
    if len(new_table) == 0:
        new_table = table
        real_selected_columns = ["*"]
    new_table = twoD_list_transpose(new_table)

    table_info["table_text"] = new_table
    table_info["act_chain"].append(
        f"f_select_column({', '.join(real_selected_columns)})"
    )

    return table_info
