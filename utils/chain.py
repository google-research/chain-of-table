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
from tqdm import tqdm
import numpy as np
from utils.helper import table2string
from collections import defaultdict
import pickle
import os

import multiprocessing as mp

from operations import *


def fixed_chain_exec_mp(llm, init_samples, fixed_op_list, n_proc=10, chunk_size=50):
    history = {}
    final_result = None

    chain_header = copy.deepcopy(init_samples)
    chain_key = ""

    for i, (op_name, solver_func, kargs, llm_kargs) in enumerate(fixed_op_list):
        chain_key += f"->{op_name}" if i > 0 else op_name
        chain_header = conduct_single_solver_mp(
            llm=llm,
            all_samples=chain_header,
            solver_func=solver_func,
            tqdm_tag=op_name,
            n_proc=n_proc,
            chunk_size=chunk_size,
            llm_options=llm.get_model_options(
                **llm_kargs,
            ),
            **kargs,
        )

        history[f"({i}) {chain_key}"] = chain_header
        if i == len(fixed_op_list) - 1:
            final_result = chain_header

    return final_result, history


def conduct_single_solver(llm, all_samples, solver_func, tqdm_tag=None, **kwargs):
    result_samples = [None for _ in range(len(all_samples))]

    for idx in tqdm(range(len(all_samples)), desc=tqdm_tag):
        try:
            sample = all_samples[idx]
            table_info = get_table_info(
                sample,
                skip_op=kwargs.get("skip_op", []),
                first_n_op=kwargs.get("first_n_op", None),
            )
            proc_sample = solver_func(sample, table_info, llm, **kwargs)
            result_samples[idx] = proc_sample
        except Exception as e:
            print(f"Error in {idx}th sample: {e}")
            continue
    return result_samples


def _conduct_single_solver_mp_core(arg):
    idx, sample, llm, solver_func, kwargs = arg
    try:
        table_info = get_table_info(
            sample,
            skip_op=kwargs.get("skip_op", []),
            first_n_op=kwargs.get("first_n_op", None),
        )
        proc_sample = solver_func(sample, table_info, llm, **kwargs)
        return idx, proc_sample
    except Exception as e:
        print(f"Error in {idx}-th sample: {e}")
        return idx, None


def conduct_single_solver_mp(
    llm, all_samples, solver_func, tqdm_tag=None, n_proc=10, chunk_size=50, **kwargs
):
    result_samples = [None for _ in range(len(all_samples))]

    args = [
        (idx, sample, llm, solver_func, kwargs)
        for idx, sample in enumerate(all_samples)
    ]

    with mp.Pool(n_proc) as p:
        for idx, proc_sample in tqdm(
            p.imap_unordered(_conduct_single_solver_mp_core, args, chunksize=chunk_size),
            total=len(all_samples),
            desc=tqdm_tag,
        ):
            result_samples[idx] = proc_sample

    return result_samples


def get_act_func(name):
    try:
        return eval(f"{name}_act")
    except:

        def _default_act(table_text, *args, **kwargs):
            return copy.deepcopy(table_text)

        if "query" not in name:
            print("Unknown operation: ", name)
        return _default_act


def get_table_info(sample, skip_op=[], first_n_op=None):
    table_text = sample["table_text"]
    chain = sample["chain"]

    if first_n_op is not None:
        chain = chain[:first_n_op]

    table_info = {
        "table_text": table_text,
        "act_chain": [],
    }

    for operation in chain:
        operation_name = operation["operation_name"]
        act_func = get_act_func(operation_name)
        table_info = act_func(table_info, operation, skip_op=skip_op)

    return table_info


def get_table_log(sample, skip_op=[], first_n_op=None):
    table_text = sample["table_text"]
    chain = sample["chain"]

    if first_n_op is not None:
        chain = chain[:first_n_op]

    table_log = []

    table_info = {
        "table_text": table_text,
        "act_chain": [],
    }
    table_log.append(table_info)

    for operation in chain:
        operation_name = operation["operation_name"]    
        act_func = get_act_func(operation_name)
        table_info = act_func(table_info, operation, skip_op=skip_op)
        if 'row' in operation_name:
            table_info['act_chain'][-1] = table_info['_real_select_rows']
        if 'query' in operation_name:
            table_info['act_chain'].append(f'{operation_name}()')
            table_info['cotable_result'] = operation['parameter_and_conf'][0][0]
        table_log.append(table_info)

    return table_log


# Dynmiac Chain Func


plan_add_column_demo = """If the table does not have the needed column to tell whether the statement is True or False, we use f_add_column() to add a new column for it. For example,
/*
col : rank | lane | player | time
row 1 :  | 5 | olga tereshkova (kaz) | 51.86
row 2 :  | 6 | manjeet kaur (ind) | 52.17
row 3 :  | 3 | asami tanno (jpn) | 53.04
*/
Statement: there are one athlete from japan.
Function: f_add_column(country of athlete)
Explanation: The statement is about the number of athletes from japan. We need to known the country of each athlete. There is no column of the country of athletes. We add a column "country of athlete"."""

plan_select_column_demo = """If the table only needs a few columns to tell whether the statement is True or False, we use f_select_column() to select these columns for it. For example,
/*
col : code | county | former province | area (km2) | population | capital
row 1 : 1 | mombasa | coast | 212.5 | 939,370 | mombasa (city)
row 2 : 2 | kwale | coast | 8,270.3 | 649,931 | kwale
row 3 : 3 | kilifi | coast | 12,245.9 | 1,109,735 | kilifi
*/
Statement: momasa is a county with population higher than 500000.
Function: f_select_column(county, population)
Explanation: The statement wants to check momasa county with population higher than 500000. We need to know the county and its population. We select the column "county" and column "population"."""

plan_select_row_demo = """If the table only needs a few rows to tell whether the statement is True or False, we use f_select_row() to select these rows for it. For example,
/*
table caption : jeep grand cherokee.
col : years | displacement | engine | power | torque
row 1 : 1999 - 2004 | 4.0l (242cid) | power tech i6 | - | 3000 rpm
row 2 : 1999 - 2004 | 4.7l (287cid) | powertech v8 | - | 3200 rpm
row 3 : 2002 - 2004 | 4.7l (287cid) | high output powertech v8 | - | -
row 4 : 1999 - 2001 | 3.1l diesel | 531 ohv diesel i5 | - | -
row 5 : 2002 - 2004 | 2.7l diesel | om647 diesel i5 | - | -
*/
Statement: the jeep grand cherokee with the om647 diesel i5 had the third lowest numbered displacement.
Function: f_select_row(row 1, row 4, row 5)
Explanation: The statement wants to check the om647 diesel i5 had third lowest numbered displacement. We need to know the first three low numbered displacement and all rows that power is om647 diesel i5. We select the row 1, row 4, row 5."""

plan_group_column_demo = """If the statement is about items with the same value and the number of these items, we use f_group_column() to group the items. For example,
/*
col : district | name | party | residence | first served
row 1 : district 1 | nelson albano | dem | vineland | 2006
row 2 : district 1 | robert andrzejczak | dem | middle twp. | 2013†
row 3 : district 2 | john f. amodeo | rep | margate | 2008
*/
Statement: there are 5 districts are democratic
Function: f_group_column(party)
Explanation: The statement wants to check 5 districts are democratic. We need to know the number of dem in the table. We group the rows according to column "party"."""

plan_sort_column_demo = """If the statement is about the order of items in a column, we use f_sort_column() to sort the items. For example,
/*
col : position | club | played | points
row 1 : 1 | malaga cf | 42 | 79
row 10 : 10 | cp merida | 42 | 59
row 3 : 3 | cd numancia | 42 | 73
*/
Statement: cd numancia placed in the last position.
Function: f_sort_column(position)
Explanation: The statement wants to check about cd numancia in the last position. We need to know the order of position from last to front. We sort the rows according to column "position"."""

plan_full_demo_simple = """Here are examples of using the operations to tell whether the statement is True or False.

/*
col : date | division | league | regular season | playoffs | open cup | avg. attendance
row 1 : 2001/01/02 | 2 | usl a-league | 4th, western | quarterfinals | did not qualify | 7,169
row 2 : 2002/08/06 | 2 | usl a-league | 2nd, pacific | 1st round | did not qualify | 6,260
row 5 : 2005/03/24 | 2 | usl first division | 5th | quarterfinals | 4th round | 6,028
*/
Statement: 2005 is the last year where this team was a part of the usl a-league?
Function Chain: f_add_column(year) -> f_select_row(row 1, row 2) -> f_select_column(year, league) -> f_sort_column(year) -> <END>

*/
col : rank | lane | athlete | time
row 1 : 1 | 6 | manjeet kaur (ind) | 52.17
row 2 : 2 | 5 | olga tereshkova (kaz) | 51.86
row 3 : 3 | 4 | pinki pramanik (ind) | 53.06
*/
Statement: There are 10 athletes from India.
Function Chain: f_add_column(country of athletes) -> f_select_row(row 1, row 3) -> f_select_column(athlete, country of athletes) -> f_group_column(country of athletes) -> <END>

/*
col : week | when | kickoff | opponent | results; final score | results; team record | game site | attendance
row 1 : 1 | saturday, april 13 | 7:00 p.m. | at rhein fire | w 27–21 | 1–0 | rheinstadion | 32,092
row 2 : 2 | saturday, april 20 | 7:00 p.m. | london monarchs | w 37–3 | 2–0 | waldstadion | 34,186
row 3 : 3 | sunday, april 28 | 6:00 p.m. | at barcelona dragons | w 33–29 | 3–0 | estadi olímpic de montjuïc | 17,503
*/
Statement: the competition with highest points scored is played on April 20.
Function Chain: f_add_column(points scored) -> f_select_row(*) -> f_select_column(when, points scored) -> f_sort_column(points scored) -> <END>

/*
col : iso/iec standard | status | wg
row 1 : iso/iec tr 19759 | published (2005) | 20
row 2 : iso/iec 15288 | published (2008) | 7
row 3 : iso/iec 12207 | published (2011) | 7
*/
Statement: 2 standards are published in 2011
Function Chain: f_add_column(year) -> f_select_row(row 3) -> f_select_column(year) -> f_group_column(year) -> <END>

Here are examples of using the operations to tell whether the statement is True or False."""

possible_next_operation_dict = {
    "<init>": [
        "add_column", 
        "select_row", 
        "select_column",
        "group_column",
        "sort_column",
    ],
    "add_column": [
        "select_row",
        "select_column", 
        "group_column", 
        "sort_column",
        "<END>",
    ],
    "select_row": [
        "select_column",
        "group_column",
        "sort_column",
        "<END>",
    ],
    "select_column": [
        "group_column",
        "sort_column",
        "<END>",
    ],
    "group_column": [
        "sort_column",
        "<END>",
    ],
    "sort_column": [
        "<END>",
    ],
}


def get_operation_name(string):
    # f_xxxx(...)
    res = re.findall(r"f_(.*?)\(.*\)", string)[0]
    return res


def get_all_operation_names(string):
    operation_names = []
    parts = string.split("->")
    for part in parts:
        part = part.strip()
        if part == "<END>":
            operation_names.append("<END>")
        else:
            res = re.findall(r"f_(.*?)\(.*\)", part)
            if res:
                operation_names.append(res[0])
    return operation_names


def generate_prompt_for_next_step(
    sample,
    debug=False,
    llm=None,
    llm_options=None,
    strategy="top",
):
    table_info = get_table_info(sample)
    act_chain = table_info["act_chain"]

    if debug:
        print("Act Chain: ", act_chain, flush=True)

    kept_act_chain = [x for x in act_chain if not x.startswith("skip")]
    kept_act_chain_str = " -> ".join(kept_act_chain)
    if kept_act_chain_str:
        kept_act_chain_str += " ->"

    skip_act_chain = [x for x in act_chain if x.startswith("skip")]
    skip_act_chain_op_names = []
    for op in skip_act_chain:
        op = op[len("skip ") :]
        op_name = get_operation_name(op)
        skip_act_chain_op_names.append(op_name)

    if debug:
        print("Kept Act Chain: ", kept_act_chain, flush=True)
        print("Skip Act Chain: ", skip_act_chain, flush=True)

    last_operation = (
        "<init>" if not kept_act_chain else get_operation_name(kept_act_chain[-1])
    )
    possible_next_operations = possible_next_operation_dict[last_operation]
    possible_next_operations = [
        x for x in possible_next_operations if x not in skip_act_chain_op_names
    ]

    if debug:
        print("Last Operation: ", last_operation, flush=True)
        print("Possible Next Operations: ", possible_next_operations, flush=True)

    if len(possible_next_operations) == 1:
        log = {
            "act_chain": act_chain,
            "last_operation": last_operation,
            "possible_next_operations": possible_next_operations,
            "prompt": None,
            "response": None,
            "generate_operations": None,
            "next_operation": possible_next_operations[0],
        }
        return possible_next_operations[0], log

    prompt = ""
    for operation in possible_next_operations:
        if operation == "<END>":
            continue
        prompt += eval(f"plan_{operation}_demo") + "\n\n"

    prompt += plan_full_demo_simple + "\n\n"

    prompt += "/*\n" + table2string(table_info["table_text"]) + "\n*/\n"
    prompt += "Statement: " + sample["statement"] + "\n"

    _possible_next_operations_str = " or ".join(
        [f"f_{op}()" if op != "<END>" else op for op in possible_next_operations]
    )

    if len(possible_next_operations) > 1:
        prompt += (
            f"The next operation must be one of {_possible_next_operations_str}.\n"
        )
    else:
        prompt += f"The next operation must be {_possible_next_operations_str}.\n"

    prompt += "Function Chain: " + kept_act_chain_str

    responses = llm.generate_plus_with_score(
        prompt, options=llm_options, end_str="\n\n"
    )

    if strategy == "top":
        response = responses[0][0]
        generate_operations = get_all_operation_names(response)
        if debug:
            print('Prompt:', prompt.split("\n\n")[-1])
            print('Response:', response)
            print("Generated Operations: ", generate_operations)
        next_operation = "<END>"
        for operation in generate_operations:
            if operation in possible_next_operations:
                next_operation = operation
                break
    elif strategy == "voting":
        next_operation_conf_dict = defaultdict(float)
        for response, score in responses:
            generate_operations = get_all_operation_names(response)
            next_operation = None
            for operation in generate_operations:
                if operation in possible_next_operations:
                    next_operation = operation
                    break
            if next_operation:
                next_operation_conf_dict[next_operation] += np.exp(score)
        if len(next_operation_conf_dict) != 0:
            next_operation_conf_pairs = sorted(
                next_operation_conf_dict.items(), key=lambda x: x[1], reverse=True
            )
            next_operation = next_operation_conf_pairs[0][0]
        else:
            next_operation = "<END>"

    log = {
        "act_chain": act_chain,
        "last_operation": last_operation,
        "possible_next_operations": possible_next_operations,
        "prompt": prompt,
        "response": response,
        "generate_operations": generate_operations,
        "next_operation": next_operation,
    }

    return next_operation, log


def dynamic_chain_exec_one_sample(
    sample,
    llm,
    llm_options=None,
    strategy="top",
    debug=False,
    operation_parameter_dict=None,
):
    if operation_parameter_dict is None:
        operation_parameter_dict = {
            "add_column": (
                "addColumn",
                add_column_func,
                {},
                llm.get_model_options(
                    temperature=0.0,
                    per_example_max_decode_steps=150,
                    per_example_top_p=1.0,
                ),
            ),
            "select_row": (
                "selectRow",
                select_row_func,
                {},
                llm.get_model_options(
                    temperature=0.5,
                    per_example_max_decode_steps=150,
                    per_example_top_p=1.0,
                    n_sample=8,
                ),
            ),
            "select_column": (
                "selectColumn",
                select_column_func,
                {},
                llm.get_model_options(
                    temperature=0.5,
                    per_example_max_decode_steps=150,
                    per_example_top_p=1.0,
                    n_sample=8,
                ),
            ),
            "group_column": (
                "groupColumn",
                group_column_func,
                dict(skip_op=[]),
                llm.get_model_options(
                    temperature=0.0,
                    per_example_max_decode_steps=150,
                    per_example_top_p=1.0,
                ),
            ),
            "sort_column": (
                "sortColumn",
                sort_column_func,
                dict(skip_op=[]),
                llm.get_model_options(
                    temperature=0.0,
                    per_example_max_decode_steps=150,
                    per_example_top_p=1.0,
                ),
            ),
        }

    dynamic_chain_log = []

    current_sample = copy.deepcopy(sample)
    while True:
        # generate next operation
        next_operation, log = generate_prompt_for_next_step(
            current_sample,
            llm=llm,
            llm_options=llm_options,
            strategy=strategy,
            debug=debug,
        )
        dynamic_chain_log.append(log)

        if debug:
            print(next_operation)

        if next_operation == "<END>":
            break

        param = operation_parameter_dict[next_operation]
        op_name, solver_func, kargs, op_llm_options = param

        table_info = get_table_info(current_sample)

        current_sample = solver_func(
            current_sample, table_info, llm=llm, llm_options=op_llm_options, **kargs
        )
    return current_sample, dynamic_chain_log


def dynamic_chain_exec_with_cache_for_loop(
    all_samples,
    llm,
    llm_options=None,
    strategy="voting",
    cache_dir="./cache/debug",
):
    os.makedirs(cache_dir, exist_ok=True)
    result_samples = [None for _ in range(len(all_samples))]
    dynamic_chain_log_list = [None for _ in range(len(all_samples))]

    cache_filename = "case-{}.pkl"

    def _func(idx):
        sample = all_samples[idx]
        sample_id = sample["id"]
        cache_path = os.path.join(cache_dir, cache_filename.format(sample_id))
        if os.path.exists(cache_path):
            _, proc_sample, log = pickle.load(open(cache_path, "rb"))
        else:
            proc_sample, log = dynamic_chain_exec_one_sample(
                sample, llm=llm, llm_options=llm_options, strategy=strategy
            )
            pickle.dump((sample, proc_sample, log), open(cache_path, "wb"))
        result_samples[idx] = proc_sample
        dynamic_chain_log_list[idx] = log

    for idx in tqdm(range(len(all_samples)), total=len(all_samples)):
        try:
            _func(idx)
        except Exception as e:
            print(f"IDX={idx}: {e}", flush=True)

    return result_samples, dynamic_chain_log_list


def _dynamic_chain_exec_with_cache_mp_core(arg):
    idx, sample, llm, llm_options, strategy, cache_dir = arg

    cache_filename = "case-{}.pkl"
    try:
        sample_id = sample["id"]
        cache_path = os.path.join(cache_dir, cache_filename.format(idx))
        if os.path.exists(cache_path):
            _, proc_sample, log = pickle.load(open(cache_path, "rb"))
        else:
            proc_sample, log = dynamic_chain_exec_one_sample(
                sample, llm=llm, llm_options=llm_options, strategy=strategy
            )
            pickle.dump((sample, proc_sample, log), open(cache_path, "wb"))
        return idx, proc_sample, log
    except Exception as e:
        print(f"Error in {sample_id}: {e}", flush=True)
        return idx, None, None


def dynamic_chain_exec_with_cache_mp(
    all_samples,
    llm,
    llm_options=None,
    strategy="voting",
    cache_dir="./results/debug",
    n_proc=10,
    chunk_size=50,
):
    os.makedirs(cache_dir, exist_ok=True)
    result_samples = [None for _ in range(len(all_samples))]
    dynamic_chain_log_list = [None for _ in range(len(all_samples))]

    args = [
        (idx, sample, llm, llm_options, strategy, cache_dir)
        for idx, sample in enumerate(all_samples)
    ]

    with mp.Pool(n_proc) as p:
        for idx, proc_sample, log in tqdm(
            p.imap_unordered(
                _dynamic_chain_exec_with_cache_mp_core, args, chunksize=chunk_size
            ),
            total=len(all_samples),
        ):
            result_samples[idx] = proc_sample
            dynamic_chain_log_list[idx] = log

    return result_samples, dynamic_chain_log_list
