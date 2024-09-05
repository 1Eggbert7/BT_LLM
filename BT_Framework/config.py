# config.py
# Alexander Leszczynski
# 21-08-2024

DEBUG = False           # True when debugging is enabled
RUNS = 4                # Number of runs for the system
BASELINE = False         # True when the baseline system is being used
MAX_LLM_CALL = 40       # Maximum number of calls to the LLM
LLM = True              # True when LLMs are being used
FURHAT = True           # True when Furhat is being used
FURHAT_IP_ADDRESS = "192.168.0.103" # IP address of the robot
FURHAT_VOICE_NAME = 'Gregory-Neural'  # Voice name of the robot
EXPLAIN = False          # True when explanations are being used
VERSION = "1.3"          # Version of the system
RENDER = False           # True when rendering BT is enabled
FURHAT_INIT = False      # True when Furhat is being initialized 