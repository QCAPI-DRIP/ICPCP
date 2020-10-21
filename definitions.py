import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
K8_CONFIG_PATH = os.path.join(ROOT_DIR, 'external_apis', 'config', 'config')
ENDPOINTS_PATH = os.path.join(ROOT_DIR, 'endpoints')
PLANNING_INPUT = os.path.join(ROOT_DIR, 'planning_input')
PLANNING_OUTPUT = os.path.join(ROOT_DIR, 'planning_output')
EXPERIMENT_LOGS = os.path.join(ROOT_DIR, 'experiment_logs')
USABILITY_STUDY_PATH = os.path.join(ROOT_DIR, 'usability_study')
TOSCA_GENERATORS = os.path.join(ROOT_DIR, 'tosca_generators')
