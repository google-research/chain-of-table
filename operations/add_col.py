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


import re
import copy
import numpy as np
from utils.helper import table2string


add_column_demo = """To tell the statement is true or false, we can first use f_add_column() to add more columns to the table.

The added columns should have these data types:
1. Numerical: the numerical strings that can be used in sort, sum
2. Datetype: the strings that describe a date, such as year, month, day
3. String: other strings

/*
col : week | when | kickoff | opponent | results; final score | results; team record | game site | attendance
row 1 : 1 | saturday, april 13 | 7:00 p.m. | at rhein fire | w 27–21 | 1–0 | rheinstadion | 32,092
row 2 : 2 | saturday, april 20 | 7:00 p.m. | london monarchs | w 37–3 | 2–0 | waldstadion | 34,186
row 3 : 3 | sunday, april 28 | 6:00 p.m. | at barcelona dragons | w 33–29 | 3–0 | estadi olímpic de montjuïc | 17,503
*/
Statement: april 20 is the date of the competition with highest attendance.
The existing columns are: "week", "when", "kickoff", "opponent", "results; final score", "results; team record", "game site", "attendance".
Explanation: To tell this statement is true or false, we need to know the attendence number of each competition. We extract the value from column "attendance" and create a different column "attendance number" for each row. The datatype is numerical.
Therefore, the answer is: f_add_column(attendance number). The value: 32092 | 34186 | 17503

/*
col : rank | lane | player | time
row 1 :  | 5 | olga tereshkova (kaz) | 51.86
row 2 :  | 6 | manjeet kaur (ind) | 52.17
row 3 :  | 3 | asami tanno (jpn) | 53.04
*/
Statement: there are one athlete from japan.
The existing columns are: rank, lane, player, time.
Explanation: To tell this statement is true or false, we need to know the country of each athelte. We extract the value from column "player" and create a different column "country of athletes" for each row. The datatype is string.
Therefore, the answer is: f_add_column(country of athletes). The value: kaz | ind | jpn

/*
col : year | competition | venue | position | notes
row 1 : 1991 | european junior championships | thessaloniki, greece | 10th | 4.90 m
row 2 : 1992 | world junior championships | seoul, south korea | 1st | 5.45 m
row 3 : 1996 | european indoor championships | stockholm, sweden | 14th (q) | 5.45 m
*/
Statement: laurens place 1st in 1991.
The existing columns are: year, competition, venue, position, notes.
Explanation: To tell this statement is true or false, we need to know the place of each competition. We extract the value from column "position" and create a different column "placing result" for each row. The datatype is numerical.
Therefore, the answer is: f_add_column(placing result). The value: 10 | 1 | 14

/*
col : iso/iec standard | status | wg
row 1 : iso/iec tr 19759 | published (2005) | 20
row 2 : iso/iec 15288 | published (2008) | 7
row 3 : iso/iec 12207 | published (2008) | 7
*/
Statement: the standards published three times in 2008.
The existing columns are: iso/iec standard, title, status, description, wg.
Explanation: To tell this statement is true or false, we need to know the year of each standard. We extract the value from column "status" and create a different column "year of standard" for each row. The datatype is datetype.
Therefore, the answer is: f_add_column(year of standard). The value: 2005 | 2008 | 2008

/*
col : match | date | ground | opponent | score1 | pos. | pts. | gd
row 1 : 1 | 15 august | a | bayer uerdingen | 3 – 0 | 1 | 2 | 3
row 2 : 2 | 22 july | h | 1. fc kaiserslautern | 1 – 0 | 1 | 4 | 4
row 3 : 4 | 29 september | h | dynamo dresden | 3 – 1 | 1 | 6 | 6
*/
Statement: they play 5 times in august.
The existing columns are: match, date, ground, opponent, score1, pos., pts., gd.
Explanation: To tell this statement is true or false, we need to know the month of each match. We extract the value from column "date" and create a different column "month" for each row. The datatype is datetype.
Therefore, the answer is: f_add_column(month). The value: august | july | september

/*
table caption : 1984 u.s. open (golf)
col : place | player | country | score | to par
row 1 : 1 | hale irwin | united states | 68 + 68 = 136 | - 4
row 2 : 2 | fuzzy zoeller | united states | 71 + 66 = 137 | -- 3
row 3 : t3 | david canipe | united states | 69 + 69 = 138 | - 2
*/
Statement: david canipe of united states has 138 score
The existing columns are: place, player, country, score, to par.
Explanation: To tell this statement is true or false, we need to know the score values of each player. We extract the value from column "score" and create a different column "score value" for each row. The datatype is numerical.
Therefore, the answer is: f_add_column(score value). The value: 136 | 137 | 138

/*
col : code | county | former province | area (km2) | population; census 2009 | capital
row 1 : 1 | mombasa | coast | 212.5 | 939,370 | mombasa (city)
row 2 : 2 | kwale | coast | 8,270.3 | 649,931 | kwale
row 3 : 3 | kilifi | coast | 12,245.9 | 1,109,735 | kilifi
*/
Statement: kwale has a population in 2009 higher than 500,000.
The existing columns are: code, county, former province, area (km2), population; census 2009, capital.
Explanation: To tell this statement is true or false, we need to know the population of each county. We extract the value from column "population; census 2009" and create a different column "population" for each row. The datatype is numerical.
Therefore, the answer is: f_add_column(population). The value: 939370 | 649311 | 1109735"""


def add_column_build_prompt(table_text, statement, table_caption=None, num_rows=100):
    table_str = table2string(table_text, caption=table_caption, num_rows=num_rows)
    prompt = "/*\n" + table_str + "\n*/\n"
    prompt += "Statement: " + statement + "\n"
    prompt += "The existing columns are: "
    prompt += ", ".join(table_text[0]) + ".\n"
    prompt += "Explanation:"
    return prompt


def add_column_func(
    sample, table_info, llm, llm_options=None, debug=False, skip_op=[], strategy="top"
):
    operation = {
        "operation_name": "add_column",
        "parameter_and_conf": [],
    }
    failure_sample_copy = copy.deepcopy(sample)
    failure_sample_copy["chain"].append(operation)

    # table_info = get_table_info(sample, skip_op=skip_op)
    table_text = table_info["table_text"]

    table_caption = sample["table_caption"]
    cleaned_statement = sample["cleaned_statement"]
    cleaned_statement = re.sub(r"\d+", "_", cleaned_statement)

    prompt = "" + add_column_demo.rstrip() + "\n\n"
    prompt += add_column_build_prompt(
        table_text, cleaned_statement, table_caption=table_caption, num_rows=3
    )
    if llm_options is None:
        llm_options = llm.get_model_options()
    llm_options["n"] = 1
    responses = llm.generate_plus_with_score(
        prompt,
        options=llm_options,
    )

    add_column_and_conf = {}
    for res, score in responses:
        try:
            f_add_func = re.findall(r"f_add_column\(.*\)", res, re.S)[0].strip()
            left = f_add_func.index("(") + 1
            right = f_add_func.index(")")
            add_column = f_add_func[left:right].strip()
            first_3_values = res.split("The value:")[-1].strip().split("|")
            first_3_values = [v.strip() for v in first_3_values]
            assert len(first_3_values) == 3
        except:
            continue

        add_column_key = str((add_column, first_3_values, res))
        if add_column_key not in add_column_and_conf:
            add_column_and_conf[add_column_key] = 0
        add_column_and_conf[add_column_key] += np.exp(score)

    if len(add_column_and_conf) == 0:
        return failure_sample_copy

    add_column_and_conf_list = sorted(
        add_column_and_conf.items(), key=lambda x: x[1], reverse=True
    )
    if strategy == "top":
        selected_add_column_key = add_column_and_conf_list[0][0]
        selected_add_column_conf = add_column_and_conf_list[0][1]
    else:
        raise NotImplementedError()

    add_column, first_3_values, llm_response = eval(selected_add_column_key)

    existing_columns = table_text[0]
    if add_column in existing_columns:
        return failure_sample_copy

    add_column_contents = [] + first_3_values

    # get following contents
    try:
        left_index = llm_response.index("We extract the value from")
        right_index = llm_response.index("The value:")
        explanaiton_beginning = llm_response[left_index:right_index] + "The value:"
    except:
        return failure_sample_copy

    def _sample_to_simple_prompt_header(table_text, num_rows=3):
        x = ""
        x += "/*\n"
        x += table2string(table_text, caption=table_caption, num_rows=num_rows) + "\n"
        x += "*/\n"
        x += "Explanation: "
        return x

    new_prompt = ""
    new_prompt += (
        _sample_to_simple_prompt_header(table_text, num_rows=3)
        + llm_response[left_index:]
    )

    headers = table_text[0]
    rows = table_text[1:]
    for i in range(3, len(rows)):
        partial_table_text = [headers] + rows[i : i + 1]
        cur_prompt = (
            new_prompt
            + "\n\n"
            + _sample_to_simple_prompt_header(partial_table_text)
            + explanaiton_beginning
        )
        cur_response = llm.generate(
            cur_prompt,
            options=llm.get_model_options(
                per_example_max_decode_steps=150, per_example_top_p=1.0
            ),
        ).strip()
        if debug:
            print(cur_prompt)
            print(cur_response)
            print("---")
            print()

        contents = cur_response
        if "|" in contents:
            contents = contents.split("|")[0].strip()

        add_column_contents.append(contents)

    if debug:
        print("New col contents: ", add_column_contents)

    add_column_info = [
        (str((add_column, add_column_contents)), selected_add_column_conf)
    ]

    operation = {
        "operation_name": "add_column",
        "parameter_and_conf": add_column_info,
    }

    sample_copy = copy.deepcopy(sample)
    sample_copy["chain"].append(operation)

    return sample_copy


def add_column_act(table_info, operation, skip_op=[], debug=False):
    table_info = copy.deepcopy(table_info)

    failure_table_info = copy.deepcopy(table_info)
    failure_table_info["act_chain"].append("skip f_add_column()")
    if "add_column" in skip_op:
        return failure_table_info
    if len(operation["parameter_and_conf"]) == 0:
        return failure_table_info

    add_column_key, _ = operation["parameter_and_conf"][0]
    add_column, add_column_contents = eval(add_column_key)

    table_text = table_info["table_text"]
    headers = table_text[0]
    rows = table_text[1:]

    header2contents = {}
    for i, header in enumerate(headers):
        header2contents[header] = []
        for row in rows:
            header2contents[header].append(row[i])

    if add_column.startswith("number of"):
        # remove 'number of'
        if debug:
            print("remove number of")
        return failure_table_info

    if len(set(add_column_contents)) == 1:
        # all same
        if debug:
            print("all same")
        return failure_table_info

    for x in add_column_contents:
        if x.strip() == "":
            # empty cell
            if debug:
                print("empty cell")
            return failure_table_info

    if add_column in headers:
        # same column header
        if debug:
            print("same column header")
        return failure_table_info

    for header in header2contents:
        if add_column_contents == header2contents[header]:
            # different header, same content
            if debug:
                print("different header, same content")
            return failure_table_info

    exist_flag = False

    for header, contents in header2contents.items():
        current_column_exist_flag = True

        for i in range(len(contents)):
            if add_column_contents[i] not in contents[i]:
                current_column_exist_flag = False
                break

        if current_column_exist_flag:
            exist_flag = True
            break
    if not exist_flag:
        if debug:
            print(add_column, add_column_contents)
            print("not substring of a column")
        return failure_table_info

    if debug:
        print("default")
    new_headers = headers + [add_column]
    new_rows = []
    for i, row in enumerate(rows):
        row.append(add_column_contents[i])
        new_rows.append(row)

    new_table_text = [new_headers] + new_rows
    table_info["table_text"] = new_table_text
    table_info["act_chain"].append(f"f_add_column({add_column})")
    return table_info
