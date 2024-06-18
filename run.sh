if [[ -z "$OPENAI_KEY" ]]; then
    read -p "OPENAI_KEY env not found. Enter your OpenAI API key: " openai_api_key
    if [[ -z "$openai_api_key" ]]; then
        echo "No API key entered. Exiting..."
        exit 1
    fi
else
    openai_api_key="$OPENAI_KEY"
fi

python run_tabfact.py --result_dir 'results/tabfact_first10' --first_n 5 --n_proc 1 --chunk_size 1 --openai_api_key "$openai_api_key"