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
import numpy as np
from utils.helper import table2string


general_demo = """/*
table caption : 2008 sidecarcross world championship.
col : position | driver / passenger | equipment | bike no | points
row 1 : 1 | daniël willemsen / reto grütter | ktm - ayr | 1 | 531
row 2 : 2 | kristers sergis / kaspars stupelis | ktm - ayr | 3 | 434
row 3 : 3 | jan hendrickx / tim smeuninx | zabel - vmc | 2 | 421
row 4 : 4 | joris hendrickx / kaspars liepins | zabel - vmc | 8 | 394
row 5 : 5 | marco happich / meinrad schelbert | zabel - mefo | 7 | 317
*/
Statement: bike number 3 is the only one to use equipment ktm - ayr.
The anwser is: NO

/*
table caption : 1957 vfl season.
col : home team | home team score | away team | away team score | venue | crowd | date
row 1 : footscray | 6.6 (42) | north melbourne | 8.13 (61) | western oval | 13325 | 10 august 1957
row 2 : essendon | 10.15 (75) | south melbourne | 7.13 (55) | windy hill | 16000 | 10 august 1957
row 3 : st kilda | 1.5 (11) | melbourne | 6.13 (49) | junction oval | 17100 | 10 august 1957
row 4 : hawthorn | 14.19 (103) | geelong | 8.7 (55) | brunswick street oval | 12000 | 10 august 1957
row 5 : fitzroy | 8.14 (62) | collingwood | 8.13 (61) | glenferrie oval | 22000 | 10 august 1957
*/
Statement: collingwood was the away team playing at the brunswick street oval venue.
The anwser is: NO

/*
table caption : co - operative commonwealth federation (ontario section).
col : year of election | candidates elected | of seats available | of votes | % of popular vote
row 1 : 1934 | 1 | 90 | na | 7.0%
row 2 : 1937 | 0 | 90 | na | 5.6%
row 3 : 1943 | 34 | 90 | na | 31.7%
row 4 : 1945 | 8 | 90 | na | 22.4%
row 5 : 1948 | 21 | 90 | na | 27.0%
*/
Statement: the 1937 election had a % of popular vote that was 1.4% lower than that of the 1959 election.
The anwser is: NO

/*
table caption : 2003 pga championship.
col : place | player | country | score | to par
row 1 : 1 | shaun micheel | united states | 69 + 68 = 137 | - 3
row 2 : t2 | billy andrade | united states | 67 + 72 = 139 | - 1
row 3 : t2 | mike weir | canada | 68 + 71 = 139 | - 1
row 4 : 4 | rod pampling | australia | 66 + 74 = 140 | e
row 5 : t5 | chad campbell | united states | 69 + 72 = 141 | + 1
*/
Statement: phil mickelson was one of five players with + 1 to par , all of which had placed t5.
The anwser is: YES"""


def simple_query(sample, table_info, llm, debug=False, use_demo=False, llm_options=None):
    table_text = table_info["table_text"]

    caption = sample["table_caption"]
    statement = sample["statement"]

    prompt = ""
    prompt += "Here are the statement about the table and the task is to tell whether the statement is True or False.\n"
    prompt += "If the statement is true, answer YES, and otherwise answer NO.\n"

    if use_demo:
        prompt += "\n"
        prompt += general_demo + "\n\n"
        prompt += "Here are the statement about the table and the task is to tell whether the statement is True or False.\n"
        prompt += "If the statement is true, answer YES, and otherwise answer NO.\n"
        prompt += "\n"

    prompt += "/*\n"
    prompt += table2string(table_text, caption=caption) + "\n"
    prompt += "*/\n"

    if "group_sub_table" in table_info:
        group_column, group_info = table_info["group_sub_table"]
        prompt += "/*\n"
        prompt += "Group the rows according to column: {}.\n".format(group_column)
        group_headers = ["Group ID", group_column, "Count"]
        group_rows = []
        for i, (v, count) in enumerate(group_info):
            if v.strip() == "":
                v = "[Empty Cell]"
            group_rows.append([f"Group {i+1}", v, str(count)])
        prompt += " | ".join(group_headers) + "\n"
        for row in group_rows:
            prompt += " | ".join(row) + "\n"
        prompt += "*/\n"

    prompt += "Statement: " + statement + "\n"

    prompt += "The answer is:"
    responses = llm.generate_plus_with_score(prompt, options=llm_options)
    responses = [(res.strip(), np.exp(score)) for res, score in responses]

    if debug:
        print(prompt)
        print(responses)

    operation = {
        "operation_name": "simple_query",
        "parameter_and_conf": responses,
    }
    sample_copy = copy.deepcopy(sample)
    sample_copy["chain"].append(operation)

    return sample_copy

