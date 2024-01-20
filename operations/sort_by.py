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


sort_column_demo = """To tell the statement is true or false, we can first use f_sort() to sort the values in a column to get the order of the items. The order can be "large to small" or "small to large".

The column to sort should have these data types:
1. Numerical: the numerical strings that can be used in sort
2. DateType: the strings that describe a date, such as year, month, day
3. String: other strings

/*
col : position | club | played | points | wins | draws | losses | goals for | goals against | goal difference
row 1 : 1 | malaga cf | 42 | 79 | 22 | 13 | 7 | 72 | 47 | +25
row 10 : 10 | cp merida | 42 | 59 | 15 | 14 | 13 | 48 | 41 | +7
row 3 : 3 | cd numancia | 42 | 73 | 21 | 10 | 11 | 68 | 40 | +28
*/
Statement: cd numancia placed in the last position
The existing columns are: position, club, played, points, wins, draws, losses, goals for, goals against, goal difference.
Explanation: the statement wants to check cd numanica is in the last position. Each row is about a club. We need to know the order of position from last to front. There is a column for position and the column name is position. The datatype is Numerical.
Therefore, the answer is: f_sort(position), the order is "large to small".

/*
col : year | team | games | combined tackles | tackles | assisted tackles |
row 1 : 2004 | hou | 16 | 63 | 51 | 12 |
row 2 : 2005 | hou | 12 | 35 | 24 | 11 |
row 3 : 2006 | hou | 15 | 26 | 19 | 7 |
*/
Statement: in 2006 babin had the least amount of tackles
The existing columns are: year, team, games, combined tackles, tackles, assisted tackles.
Explanation: the statement wants to check babin had the least amount of tackles in 2006. Each row is about a year. We need to know the order of tackles from the least to the most. There is a column for tackles and the column name is tackles. The datatype is Numerical.
Therefore, the answer is: f_sort(tackles), the order is "small to large"."""


def only_keep_num_and_first_dot(s):
    if s.strip() and s.strip()[0] == "-":
        minus = True
    else:
        minus = False
    ns = ""
    dot = False
    for c in s:
        if c in "0123456789":
            ns += c
        if c == ".":
            if dot == False:
                ns += c
                dot = True
    if ns == ".":
        return ""
    if ns == "":
        return ""
    if minus:
        ns = "-" + ns
    return ns


def sort_column_build_prompt(table_text, statement, table_caption=None, num_rows=100):
    table_str = table2string(
        table_text, caption=table_caption, num_rows=num_rows
    ).strip()
    prompt = "/*\n" + table_str + "\n*/\n"
    prompt += "Statement: " + statement + "\n"
    prompt += "The existing columns are: "
    prompt += ", ".join(table_text[0]) + ".\n"
    prompt += "Explanation:"
    return prompt


def sort_column_func(
    sample, table_info, llm, llm_options=None, debug=False, skip_op=[]
):
    # table_info = get_table_info(sample, skip_op=skip_op)
    table_text = table_info["table_text"]

    statement = sample["statement"]
    prompt = "" + sort_column_demo.rstrip() + "\n\n"
    prompt += sort_column_build_prompt(table_text, statement, num_rows=3)
    responses = llm.generate_plus_with_score(
        prompt,
        options=llm_options,
    )

    if debug:
        print(prompt)
        print(responses)

    sort_info_and_conf = {}

    headers = table_text[0]
    rows = table_text[1:]
    for res, score in responses:
        try:
            datatype = re.findall(r"The datatype is (\w*).", res, re.S)[0].strip()
            sort_order = re.findall(r'the order is "(.*)"\.', res, re.S)[0].strip()
            sort_column = re.findall(r"f_sort\((.*)\)", res, re.S)[0].strip()
        except:
            continue

        if sort_order not in ["small to large", "large to small"]:
            continue
        if sort_column not in headers:
            continue
        sort_key = (sort_column, sort_order, datatype)
        if sort_key not in sort_info_and_conf:
            sort_info_and_conf[sort_key] = 0
        sort_info_and_conf[sort_key] += np.exp(score)

    sort_param_and_conf_list = []
    for (sort_column, sort_order, datatype), conf in sort_info_and_conf.items():
        sort_column_contents = []
        index = headers.index(sort_column)
        for row in rows:
            sort_column_contents.append(row[index])

        vs_to_sort = []
        vs_not_to_sort = []
        if datatype == "Numerical":
            for i in range(len(sort_column_contents)):
                v_str = sort_column_contents[i]
                v_str = only_keep_num_and_first_dot(v_str)
                if v_str == "" or v_str == ".":
                    vs_not_to_sort.append((sort_column_contents[i], i))
                else:
                    vs_to_sort.append((float(v_str), i))
        else:
            for i in range(len(sort_column_contents)):
                v_str = sort_column_contents[i]
                v_str = v_str.strip()
                if v_str == "":
                    vs_not_to_sort.append((sort_column_contents[i], i))
                else:
                    vs_to_sort.append((v_str, i))

        #  check if already sorted
        pure_vs_to_sort = [x[0] for x in vs_to_sort]
        if (
            sorted(pure_vs_to_sort) == pure_vs_to_sort
            or sorted(pure_vs_to_sort, reverse=True) == pure_vs_to_sort
        ):
            continue

        # get sorted index
        if sort_order == "small to large":
            vs_to_sort = sorted(vs_to_sort, key=lambda x: x[0])
        else:
            vs_to_sort = sorted(vs_to_sort, reverse=True, key=lambda x: x[0])
        index_order = [x[1] for x in vs_to_sort] + [x[1] for x in vs_not_to_sort]

        sort_param_and_conf_list.append(
            (
                sort_column,
                sort_order,
                datatype,
                index_order,
                max([x[0] for x in vs_to_sort]),
                min([x[0] for x in vs_to_sort]),
                conf,
            )
        )

    sort_param_and_conf_list = sorted(sort_param_and_conf_list, key=lambda x: x[-1])

    operation = {
        "operation_name": "sort_column",
        "parameter_and_conf": sort_param_and_conf_list,
    }

    sample_copy = copy.deepcopy(sample)
    sample_copy["chain"].append(operation)

    if debug:
        print(sort_param_and_conf_list)

    return sample_copy


def sort_column_act(
    table_info, operation, strategy="top", filter="Only Numerical", skip_op=[]
):
    table_info = copy.deepcopy(table_info)

    failure_table_info = copy.deepcopy(table_info)
    failure_table_info["act_chain"].append("skip f_sort_column()")

    if "sort_column" in skip_op:
        return failure_table_info
    if len(operation["parameter_and_conf"]) == 0:
        return failure_table_info

    if strategy == "top":
        sort_column, sort_order, datatype, index_order, max_v, min_v = operation[
            "parameter_and_conf"
        ][0][:-1]
    else:
        raise NotImplementedError()

    if filter == "Only Numerical":
        if datatype != "Numerical":
            return failure_table_info
    else:
        raise NotImplementedError()

    table_text = table_info["table_text"]
    headers = table_text[0]
    rows = table_text[1:]
    new_rows = [rows[i] for i in index_order]
    new_table_text = [headers] + new_rows

    table_info["table_text"] = new_table_text
    table_info["sort_sub_table"] = (sort_column, max_v, min_v)
    table_info["act_chain"].append(f"f_sort_column({sort_column})")

    return table_info
