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


def tabfact_match_func(sample, strategy="top"):
    results = sample["chain"][-1]["parameter_and_conf"]

    if strategy == "top":
        res = results[0][0]
    elif strategy == "weighted":
        res_conf_dict = {}
        for res, conf in results:
            if res not in res_conf_dict:
                res_conf_dict[res] = 0
            res_conf_dict[res] += conf
        res_conf_rank = sorted(res_conf_dict.items(), key=lambda x: x[1], reverse=True)
        res = res_conf_rank[0][0]
    else:
        raise NotImplementedError

    res = res.lower()
    if res == "true":
        res = "yes"
    if res == "false":
        res = "no"
    if res == "yes" and sample["label"] == 1:
        return True
    elif res == "no" and sample["label"] == 0:
        return True
    else:
        return False


def tabfact_match_func_for_samples(all_samples, strategy="top"):
    correct_list = []
    for sample in all_samples:
        try:
            if tabfact_match_func(sample, strategy):
                correct_list.append(1)
            else:
                correct_list.append(0)
        except:
            print(f"Error")
            continue
    return sum(correct_list) / len(correct_list)
