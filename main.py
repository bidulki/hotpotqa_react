import re
import os
import pandas as pd
import argparse

from agent import ReactAgent
from loader import (
    load_data,
    load_config,
    load_embedding_model,
    load_wiki_index,
    load_explorer
)

from writer import (
    write_result,
    write_message,
    write_metric,
    write_prompt
)

from utils import (
    normalize_answer,
    make_df,
    evaluate
)

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--output-dir', type=str, required=True)
    args = parser.parse_args()

    # load model and data 
    config = load_config("./config/config.yaml")
    test_data = load_data(config['path']['test_path'])
    if config['params']['search_engine'] == 'Faiss':
        print(f"Search engine: Faiss")
        embedding_model = load_embedding_model(config['path']['retriever_model'])
        explorer = load_explorer(config['path']['faiss_index_path'], embedding_model)
    else:
        print(f"Search engine: BM25")
        embedding_model = None
        explorer = None
    wiki_index = load_wiki_index(config['path']['wiki_index_path'])

    test_df = make_df(test_data)
    # run evaluation
    agent = ReactAgent(dataset=test_data,
                    df=test_df,
                    wiki_index=wiki_index, 
                    search_engine=config['params']['search_engine'],
                    explorer=explorer, 
                    model=config['params']['model'], 
                    max_step=config['params']['max_step'])

    border = "#######################################"
    message_logs = []

    for i in range(len(test_data)):
        message_logs.append(border)
        print(border)
        message_logs.append(f"EVAL_IDX: {i}")
        print(message_logs[-1])
        message_logs_tmp, test_df = agent.eval_hotpotqa(i)

        for log in message_logs_tmp:
            message_logs.append(log)

    # calculate metric
    answer_metric, sp_metric = evaluate(test_df)

    # save results
    test_name = args.output_dir
    dir_path = f"./logs/{test_name}"
    os.makedirs(dir_path, exist_ok=True)
    write_result(dir_path, test_df)
    write_message(dir_path, message_logs)
    write_metric(dir_path, answer_metric, sp_metric)
    write_prompt(dir_path)
    

if __name__ == "__main__":
    main()



