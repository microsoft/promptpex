import streamlit as st
import time, io, re, csv
import pandas as pd
from dotenv import load_dotenv, set_key

import sys
sys.path.insert(0, '..')

from src import InputSpec, StringFrontEnd, LLMFrontEnd, Module, TestCaseGenerator, AskLLMTestValidator, Mutator, Dbg, SemanticDiff, Utils, InputSpec
import pathlib
from openai import AzureOpenAI

st.set_page_config(page_title="PromptPex", layout="wide")
st.title("PromptPex: Prompt Exploration")

st.markdown("""
    <style>
    html, body, [class*="css"] {
        font-family: "Arial", sans-serif;
        background-color: #F7F7F7;
        color: #333333;
    }

    h2 {
        font-size: 24px;
    }

    body {
        gap: 1px !important;
    }

    header {
        background: transparent !important;
    }

    .block-container {
        padding-top: 0px !important;
    }

    td, th {
        font-family: Arial, sans-serif;
        font-size: 12px;
        font-weight: 100;
    }
    button.st-emotion-cache-1huvf7z.ef3psqc6 {
        display: block;
        visibility: hidden;
    }
    </style>
    """, unsafe_allow_html=True)

if 'submit_clicked' not in st.session_state:
    st.session_state['submit_clicked'] = False
if 'gen_tests_clicked' not in st.session_state:
    st.session_state['gen_tests_clicked'] = False
if 'run_tests_clicked' not in st.session_state:
    st.session_state['run_tests_clicked'] = False

if 'api_key' not in st.session_state:
    st.session_state['api_key'] = ''
if 'endpoint' not in st.session_state:
    st.session_state['endpoint'] = ''

if 'num_rules' not in st.session_state:
    st.session_state['num_rules'] = 0
if 'num_tests' not in st.session_state:
    st.session_state['num_tests'] = 0

if 'rules' not in st.session_state:
    st.session_state['rules'] = None
if 'input_spec' not in st.session_state:
    st.session_state['input_spec'] = None
if 'tests' not in st.session_state:
    st.session_state['tests'] = None
if 'test_results' not in st.session_state:
    st.session_state['test_results'] = None

if 'dir_name' not in st.session_state:
    st.session_state['dir_name'] = None
if 'module' not in st.session_state:
    st.session_state['module'] = None
if 'system_prompt' not in st.session_state:
    st.session_state['system_prompt'] = None

# col1, col2 = st.columns([7, 3])

with st.sidebar:
    st.header("API Configuration")
    st.session_state['api_key'] = st.text_input(
        'Enter your API key', type="password", value=st.session_state['api_key']
    )
    st.session_state['endpoint'] = st.text_input(
        'Enter the endpoint', value=st.session_state['endpoint']
    )
    st.session_state['num_rules'] = st.number_input(
        'Enter the number of rules to generate', 0, placeholder="max"
    )
    st.caption("Note: If the number of rules is set to 0, all rules will be generated.")
    st.session_state['num_tests'] = st.number_input(
        'Enter the number of test sets to generate', 1, placeholder="1"
    )
    st.caption("Note: If the number of tests is set to 1, tests will be generated once for all the rules.")
    

st.header("Input System Prompt")
st.session_state['system_prompt'] = st.text_area('Enter the prompt here. Now you can generate test for one prompt and then edit it and run test on the edited prompt', height=200)

# Button to submit inputs
submit_button = st.button('Start PromptPex')

if submit_button:
    st.session_state['submit_clicked'] = True
    st.session_state['gen_tests_clicked'] = False
    st.session_state['run_tests_clicked'] = False

    st.session_state['rules'] = None
    st.session_state['input_spec'] = None
    st.session_state['tests'] = None
    st.session_state['test_results'] = None

    st.session_state['dir_name'] = None
    st.session_state['module'] = None

front_end = StringFrontEnd()

# Placeholder for the specifications area
spec_placeholder = st.empty()

if st.session_state['dir_name'] is None:
    st.session_state['dir_name'] = "results" + time.strftime("%Y%m%d-%H%M%S")
    pathlib.Path(st.session_state['dir_name']).mkdir(parents=True, exist_ok=True)

if st.session_state['submit_clicked']:
    with spec_placeholder.container():  # This creates a container at the spec_placeholder location
        if st.session_state['rules'] is None:

            set_key(".env", "AZURE_OPENAI_API_KEY", st.session_state['api_key'])
            
            with open(pathlib.Path(st.session_state['dir_name'], "variant-0.txt"), "w") as f:
                f.write(st.session_state['system_prompt'])

            Dbg.set_debug_file(pathlib.Path(st.session_state['dir_name'], "log.txt"))
            original_prompt = st.session_state['system_prompt']

            rule_path = pathlib.Path(st.session_state['dir_name'], "rules-0.csv")

            with st.spinner('Extracting rules ...'):
                st.session_state['module'] = front_end.parse(st.session_state['system_prompt'], num_rules=st.session_state['num_rules'])

            st.session_state['module'].export(rule_path)

            generated_rules = pd.read_csv(rule_path)
            generated_rules_no_hash = generated_rules.copy()
            st.session_state['rules'] = generated_rules_no_hash
            st.session_state['rules'].drop(columns=['rule id'], inplace=True)   

            with st.spinner('Extracting input spec ...'):
                input_spec_path = pathlib.Path(st.session_state['dir_name'], "input_spec.csv")
                IS = InputSpec(st.session_state['system_prompt'])
                IS.export_csv(input_spec_path)
                st.session_state['input_spec'] = IS

        def update_rules(*args, **kwargs):
            updates = st.session_state['updated_rule']
            for row_id, changes in updates['edited_rows'].items():
                st.session_state['rules']['rule'].loc[int(row_id)] = changes['rule']

            rule_path = pathlib.Path(st.session_state['dir_name'], "rules-edited.csv")
            with open(rule_path, "w", encoding="utf-8", errors="ignore", newline='') as f:
                st.session_state['rules'].to_csv(f, index=False)
            
            st.session_state['module'] = Module()
            st.session_state['module'].import_rules(rule_path)

        st.header("Generated Rules")
        st.caption("Note: You can edit the rules below by double-clicking on the cell.")
        # drop 'rule id' column
        rules_edited = st.data_editor(st.session_state['rules'], key="updated_rule", use_container_width=True, on_change=update_rules)

        def update_input_spec(*args, **kwargs):
            updates = st.session_state['updated_input_spec']
            input_spec = st.session_state['input_spec'].import_csv()
            for row_id, changes in updates['edited_rows'].items():
                input_spec[int(row_id)] = changes['value']

            input_spec_path = pathlib.Path(st.session_state['dir_name'], "input-spec-edited.csv")
            with open(input_spec_path, "w", encoding="utf-8", errors="ignore", newline='') as f:
                csv_write = csv.writer(f)
                csv_write.writerow(["input spec"])
                for line in input_spec:
                    csv_write.writerow([line])

            IS = st.session_state['input_spec']
            IS.import_csv(input_spec_path)
            st.session_state['input_spec'] = IS
            

        st.header("Generated Input Spec")
        st.caption("Note: You can edit the input spec below by double-clicking on the cell.")
        st.data_editor(st.session_state['input_spec'].import_csv(), key="updated_input_spec", use_container_width=True, on_change=update_input_spec)
        # gen tests button
        gen_tests_button = st.button('Gen Tests')

        if gen_tests_button:
            st.session_state['gen_tests_clicked'] = True
            st.session_state['tests'] = None

if st.session_state['gen_tests_clicked']:
    test_path = pathlib.Path(st.session_state['dir_name'], "tests.csv")
    if st.session_state['tests'] is None:
        system_prompt = st.session_state['system_prompt']
        test_gen = TestCaseGenerator(st.session_state['module'], system_prompt, test_path, st.session_state['input_spec'].get_input_spec())
        with st.spinner('Generating tests ...'):
            tests_df = test_gen.gen_all_tests(st.session_state['num_tests'])
            display_df = pd.DataFrame(tests_df, columns=pd.Index(tests_df[0]))
            display_df.drop(columns=['Expected Output', 'Test ID',], inplace=True)
            st.session_state['tests'] = display_df[1:]
    
    st.header("Generated Tests")
    st.dataframe(st.session_state['tests'])

    run_tests_button = st.button('Run Tests')

    if run_tests_button:
        st.session_state['run_tests_clicked'] = True
        st.session_state['test_results'] = None

if st.session_state['run_tests_clicked']:
    test_path = pathlib.Path(st.session_state['dir_name'], "tests.csv")
    if st.session_state['test_results'] is None:
        original_test_run_path = pathlib.Path(st.session_state['dir_name'], "variant-run-0.csv")
        system_prompt = st.session_state['system_prompt']
        test_runner = AskLLMTestValidator(st.session_state['module'], system_prompt, system_prompt, "gpt-35-turbo", original_test_run_path)
        test_runner.append(test_path)
        with st.spinner('Running tests ...'):
            test_runner.run_tests()
        # st.session_state['test_results'] = test_runner.importResults(original_test_run_path)
        output_file_path = pathlib.Path(st.session_state['dir_name'], "variant-run-0.csv")
        # Utils.join_csv_files(test_path, original_test_run_path, "rule id", output_file_path)
        results = pd.read_csv(output_file_path)
        results.drop(columns=['rule id'], inplace=True) 
        # drop rows where 'result' is 'Passed'
        results = results[results['result'] != 'passed']
        st.session_state['test_results'] = results

    st.header("Generated Result")
    st.caption("Note: Only showing failing tests")
    st.table(st.session_state['test_results'])