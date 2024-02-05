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


import json
from tqdm import tqdm

def load_tabfact_dataset(
    dataset_path,
    raw2clean_path,
    tag="test",
    first_n=-1,
):
    tabfact_statement_raw2clean_dict = {}
    with open(raw2clean_path, "r") as f:
        lines = f.readlines()
        for line in lines:
            info = json.loads(line)
            tabfact_statement_raw2clean_dict[info["statement"]] = info["cleaned_statement"]

    dataset = []
    if first_n != -1:
        all_lines = []
        for line in open(dataset_path):
            all_lines.append(line)
            if len(all_lines) >= first_n: break
    else:
        all_lines = open(dataset_path).readlines()
    for i, line in tqdm(enumerate(all_lines), total=len(all_lines), desc=f"Loading tabfact-{tag} dataset"):
        info = json.loads(line)
        info["id"] = f"{tag}-{i}"
        info["chain"] = []
        if info["statement"] in tabfact_statement_raw2clean_dict:
            info["cleaned_statement"] = tabfact_statement_raw2clean_dict[
                info["statement"]
            ]
        else:
            info["cleaned_statement"] = info["statement"]
        dataset.append(info)
    return dataset


def wrap_input_for_demo(statement, table_caption, table_text, cleaned_statement=None):
    return {
        "statement": statement,
        "table_caption": table_caption,
        "table_text": table_text,
        "cleaned_statement": cleaned_statement if cleaned_statement is not None else statement,
        "chain": [],
    }

