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
