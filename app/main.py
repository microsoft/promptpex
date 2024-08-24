from typing import get_origin
import streamlit as st
import time, io, re, csv
import pandas as pd
from dotenv import load_dotenv, set_key

import sys
sys.path.insert(0, '..')

from src import InputSpec, StringFrontEnd, LLMFrontEnd, Module, TestCaseGenerator, AskLLMTestValidator, Mutator, Dbg, SemanticDiff, Utils, InputSpec, Mutator
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
if 'fix_clicked' not in st.session_state:
    st.session_state['fix_clicked'] = False

if 'api_key' not in st.session_state:
    st.session_state['api_key'] = ''
if 'endpoint' not in st.session_state:
    st.session_state['endpoint'] = ''

if 'num_rules' not in st.session_state:
    st.session_state['num_rules'] = 0
if 'num_tests' not in st.session_state:
    st.session_state['num_tests'] = 0
if 'num_runs' not in st.session_state:
    st.session_state['num_runs'] = 0
if 'max_fix_try' not in st.session_state:
    st.session_state['max_fix_try'] = 40
if 'fix_try' not in st.session_state:
    st.session_state['fix_try'] = 0
if 'show_passing_tests' not in st.session_state:
    st.session_state['show_passing_tests'] = False
if 'forced_temp' not in st.session_state:
    st.session_state['forced_temp'] = -1

if 'test_state' not in st.session_state:
    st.session_state['test_state'] = 0
if 'result_name' not in st.session_state:
    st.session_state['result_name'] = []

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
if 'test_model' not in st.session_state:
    st.session_state['test_model'] = "gpt-35-turbo"

if 'sp_tabs' not in st.session_state:
    st.session_state.sp_tabs = ["v1"]
    st.session_state.sp_active_tab = "v1"
    st.session_state['v1'] = ""

# col1, col2 = st.columns([7, 3])

with st.sidebar:
    st.header("Options")
    st.caption("Note: Use this button to add a new input system prompt tab.")
    if st.button("Add New System Prompt Tab"):
        new_tab_name = f"v{len(st.session_state.sp_tabs)+1}"
        st.session_state.sp_tabs.append(new_tab_name)
        st.session_state[new_tab_name] = ""

    st.session_state['num_rules'] = st.number_input(
        'Enter the number of rules to generate', 0, placeholder="max"
    )
    st.caption("Note: If the number of rules is set to 0, all rules will be generated.")
    st.session_state['num_tests'] = st.number_input(
        'Enter the number of test sets to generate', 1, placeholder="1"
    )
    st.caption("Note: If the number of tests is set to 1, tests will be generated once for all the rules.")
    st.session_state['num_runs'] = st.number_input(
    'Enter the number of times the test should run', 1, placeholder="1"
    )
    st.session_state['test_model'] = st.selectbox(
        'Select the model to run the test', ['gpt-35-turbo', 'gpt-4o', 'gpt-4o-mini', 'gpt-4-turbo', 'gpt-4', 'phi3:medium', 'phi3:mini', 'llama3.1:8b', 'gemma2:2b', 'gemma2:9b', 'mistral']
    )
    st.caption("Note: The model to run the test can be selected from the dropdown.")
    st.session_state['max_fix_try'] = st.number_input(
        'Enter the maximum number of times the fix should be tried', 1, placeholder="40"
    )
    st.caption("Note: If the number of times the fix should be tried is set to 1, only one fix will be tried.")
    st.session_state['show_passing_tests'] = st.checkbox(
        'Show passing tests', value=st.session_state['show_passing_tests']
    )
    st.caption("Note: If the show passing tests is checked, all tests results will be shown.")
    st.session_state['forced_temp'] = st.number_input(
        'Enter the forced temperature', -1.0, placeholder="-1", step=0.01
    )
    st.caption("Note: If the forced temperature is set to -1, the temperature will be calculated automatically ranging between 0 - 2 more dense around 1.")

    st.header("API Configuration")
    st.session_state['api_key'] = st.text_input(
        'Enter your API key', type="password", value=st.session_state['api_key']
    )
    st.session_state['endpoint'] = st.text_input(
        'Enter the endpoint', value=st.session_state['endpoint']
    )

st.header("Input System Prompt")

def init():
    st.session_state['submit_clicked'] = True
    st.session_state['gen_tests_clicked'] = False
    st.session_state['run_tests_clicked'] = False
    st.session_state['fix_clicked'] = False

    st.session_state['rules'] = None
    st.session_state['input_spec'] = None
    st.session_state['tests'] = None
    st.session_state['test_results'] = None

    st.session_state['dir_name'] = None
    st.session_state['module'] = None

def prompt_editor(name):
    st.session_state[name] = st.text_area('Enter the prompt here. Use the option from the sidebar (top left ">") to add a new tab', height=200, value=st.session_state[name], key=f"edit-{name}")
    if name != st.session_state.sp_active_tab:
        if st.button(f'Use {name} instead of {st.session_state.sp_active_tab} as system prompt', key=f"set-{name}"):
            st.session_state.sp_active_tab = name
            st.rerun()

sp_tabs = st.session_state.sp_tabs
tab_container = st.tabs(sp_tabs)
for i, tab in enumerate(tab_container):
    with tab:
        prompt_editor(st.session_state.sp_tabs[i])

st.session_state['system_prompt'] = st.session_state[st.session_state.sp_active_tab]

if st.button('Start PromptPex', key=f"run-"):
    init()

if st.session_state.sp_active_tab.startswith("v"):
    st.session_state['fix_try'] = 0

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

import numpy as np
def get_temp(current_index, max_index):
    if st.session_state['forced_temp'] >= 0:
        return float(st.session_state['forced_temp'])
    if max_index == 1:
        return 1.00
    values = np.linspace(-1, 1, max_index)
    # Cubing to make distribution denser around 1
    transformed_values = 1 + np.sin(values * np.pi/2)**3
    return float(transformed_values[current_index])

if st.session_state['run_tests_clicked']:
    test_path = pathlib.Path(st.session_state['dir_name'], "tests.csv")
    if st.session_state['test_results'] is None:
        original_test_run_path = pathlib.Path(st.session_state['dir_name'], f"variant-run-{st.session_state['test_state']}.csv")
        system_prompt = st.session_state['system_prompt']
        test_runner = AskLLMTestValidator(st.session_state['module'], system_prompt, system_prompt, st.session_state['test_model'], original_test_run_path)
        test_runner.append(test_path)
        with st.spinner('Running tests ...'):
            for i in range(st.session_state['num_runs']):
                temp = get_temp(i, st.session_state['num_runs'])
                test_runner.run_tests(temp)

        st.session_state['test_state'] += 1
        st.session_state['test_results'] = test_runner.all_passed()
        st.session_state['result_name'].append(f"{st.session_state.sp_active_tab}-{st.session_state['test_model']}")

    st.header("Generated Result")
    st.caption("Note: Only showing failing tests")

    tabs = [f"{st.session_state['result_name'][i]}-{i+1}" for i in range(st.session_state['test_state'])]

    tab_list = st.tabs(tabs)

    def get_original_prompt_name(idx):
        for i in range(idx, -1, -1):
            if not tabs[i].startswith("fix"):
                return tabs[i].split("-")[0]

    def get_system_prompt_history(idx):
        prompts = []
        for i in range(idx, -1, -1):
            prompt_name = tabs[i].split("-")[0]
            if prompt_name.startswith("fix"):
                prompts.append(st.session_state[tabs[i].split("-")[1]])
            else:
                prompts.append(st.session_state[prompt_name])
                break
        prompts.reverse()
        return prompts

    def get_failed_tests_history(idx):
        failed_tests = []
        for i in range(idx, -1, -1):
            prompt_name = tabs[i].split("-")[0]
            output_file_path = pathlib.Path(st.session_state['dir_name'], f"variant-run-{i}.csv")
            results = pd.read_csv(output_file_path)
            results.drop(columns=['rule id'], inplace=True)
            results = results[results['result'] != 'passed']
            # convert to list of rows as string
            results = ["\n".join([f"{col}: {row[col]}" for col in results.columns]) for index, row in results.iterrows()] 
            results = "\n".join(results)
            failed_tests.append(results)
            if not prompt_name.startswith("fix"):
                break
        failed_tests.reverse()
        return failed_tests

    for idx in range(st.session_state['test_state']):
        with tab_list[idx]:
            output_file_path = pathlib.Path(st.session_state['dir_name'], f"variant-run-{idx}.csv")
            results = pd.read_csv(output_file_path)
            results.drop(columns=['rule id'], inplace=True)
            if not st.session_state['show_passing_tests']:
                results = results[results['result'] != 'passed']
            st.table(results)

            if not results.empty:
                fix_button = False
                if tabs[idx].startswith("fix") and st.session_state['fix_try'] <= st.session_state['max_fix_try']:
                    fix_button = True
                else :
                    fix_button = st.button('Fix Prompt', key=f"fix-btn-{idx}")

                if fix_button:
                    prompts = get_system_prompt_history(idx)
                    failed_tests = get_failed_tests_history(idx)

                    assert len(prompts) == len(failed_tests)

                    name = get_original_prompt_name(idx)

                    fixed_prompt = Mutator(prompts[0]).fix_prompt(failed_tests[0], prompts[1:], failed_tests[1:], [])
                    fixed_tab_name = f"fix-{name}-{st.session_state['fix_try']}"
                    st.session_state.sp_tabs.append(fixed_tab_name)
                    st.session_state.sp_active_tab = fixed_tab_name
                    st.session_state[fixed_tab_name] = fixed_prompt
                    st.session_state['test_results'] = None
                    st.session_state['fix_try'] += 1
                    st.rerun()

# button - start fixing automatically 
# input - system prompt, tests (input, output, reason)
# getFix(system prompt, tests)
# create a new system prompt tab with the fix 
# run the tests to check if they pass 