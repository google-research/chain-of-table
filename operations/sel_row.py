# Copyright 2024 The Chain-of-Table authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import copy
import re
import numpy as np
from utils.helper import table2string


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


def select_row_build_prompt(table_text, statement, table_caption=None, num_rows=100):
    table_str = table2string(table_text, caption=table_caption).strip()
    prompt = "/*\n" + table_str + "\n*/\n"
    question = statement
    prompt += "statement : " + question + "\n"
    prompt += "explain :"
    return prompt


def select_row_func(sample, table_info, llm, llm_options=None, debug=False):
    table_text = table_info["table_text"]

    table_caption = sample["table_caption"]
    statement = sample["statement"]

    prompt = "" + select_row_demo.rstrip() + "\n\n"
    prompt += select_row_build_prompt(table_text, statement, table_caption)

    responses = llm.generate_plus_with_score(prompt, options=llm_options)

    if debug:
        print(responses)

    pattern_row = r"f_row\(\[(.*?)\]\)"

    pred_conf_dict = {}
    for res, score in responses:
        try:
            pred = re.findall(pattern_row, res, re.S)[0].strip()
        except Exception:
            continue
        pred = pred.split(", ")
        pred = [i.strip() for i in pred]
        pred = [i.split(" ")[-1] for i in pred]
        pred = sorted(pred)
        pred = str(pred)
        if pred not in pred_conf_dict:
            pred_conf_dict[pred] = 0
        pred_conf_dict[pred] += np.exp(score)

    select_row_rank = sorted(pred_conf_dict.items(), key=lambda x: x[1], reverse=True)

    operation = {
        "operation_name": "select_row",
        "parameter_and_conf": select_row_rank,
    }

    sample_copy = copy.deepcopy(sample)
    sample_copy["chain"].append(operation)

    return sample_copy


def select_row_act(table_info, operation, union_num=2, skip_op=[]):
    table_info = copy.deepcopy(table_info)

    if "select_row" in skip_op:
        failure_table_info = copy.deepcopy(table_info)
        failure_table_info["act_chain"].append("skip f_select_row()")
        return failure_table_info

    def union_lists(to_union):
        return list(set().union(*to_union))

    selected_rows_info = operation["parameter_and_conf"]
    selected_rows_info = sorted(selected_rows_info, key=lambda x: x[1], reverse=True)
    selected_rows_info = selected_rows_info[:union_num]
    selected_rows = [x[0] for x in selected_rows_info]
    selected_rows = [eval(x) for x in selected_rows]
    selected_rows = union_lists(selected_rows)

    if "*" in selected_rows:
        failure_table_info = copy.deepcopy(table_info)
        failure_table_info["act_chain"].append("f_select_row(*)")
        return failure_table_info

    real_selected_rows = []

    table_text = table_info["table_text"]
    new_table = [copy.deepcopy(table_text[0])]
    for row_id, row in enumerate(table_text):
        row_id = str(row_id)
        if row_id in selected_rows:
            new_table.append(copy.deepcopy(row))
            real_selected_rows.append(row_id)

    if len(new_table) == 1:
        failure_table_info = copy.deepcopy(table_info)
        failure_table_info["act_chain"].append("f_select_row(*)")
        return failure_table_info

    table_info["table_text"] = new_table
    selected_row_names = [f"row {x+1}" for x in range(len(real_selected_rows))]
    table_info["act_chain"].append(f"f_select_row({', '.join(selected_row_names)})")

    _real_selected_row_names = [f"row {x-1}" for x in map(int, real_selected_rows)]
    table_info['_real_select_rows'] = f"f_select_row({', '.join(_real_selected_row_names)})"

    return table_info
