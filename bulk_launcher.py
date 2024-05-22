import asyncio
from time import sleep
import subprocess
import json
import os
import re
import shutil


# Set the environment variable
os.environ['COMX_YES_TO_ALL'] = 'true'
os.environ['COMX_OUTPUT_JSON'] = 'true'



def copy_and_rename_class(filename, original_classname, new_classname):
    with open(filename, 'r') as file:
        lines = file.readlines()
    
    class_found = False
    new_lines = []
    class_lines = []
    inside_class = False
    class_indent = None
    
    for line in lines:
        new_lines.append(line)
        if not class_found and re.match(rf'^\s*class {original_classname}', line):
            class_found = True
            inside_class = True
            class_indent = re.match(r"\s*", line).group()
        
        if inside_class:
            current_indent = re.match(r"\s*", line).group()
            if current_indent == "" and len(class_lines) > 0:
                inside_class = False
            else:
                class_lines.append(line)
    
    # Rename the copied class
    if class_lines:
        class_lines[0] = class_lines[0].replace(original_classname, new_classname, 1)
        new_lines.append("\n")
        new_lines.extend(class_lines)
        new_lines.append("\n")
    else:
        raise ValueError(f"Class {original_classname} not found in {filename}")
    
    # Write the new content back to the file
    with open(filename, 'w') as file:
        file.writelines(new_lines)

# Function to validate the module path
def module_path_check(module_path):
    try: 
        if re.match(r'^[a-zA-Z_]\w*(\.[a-zA-Z_]\w*)*$', module_path):
            filename, classname = module_path.split('.')
            return filename, classname
        else:
            print("Invalid characters in module path")
            return None, None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None, None


def serve_modules(module_path, source_module, port, NumModules, Netuid):

    for i in range(NumModules):

        filename, classname = module_path_check(module_path)
        classname_instance = f"{classname}_{i}"
        module_name = f"{module_path}_{i}"
        next_port = port + i

        key_path = os.path.expanduser(f"~/.commune/key/{module_name}.json")
        if not os.path.isfile(key_path):
            subprocess.run(["comx", "key", "create", module_name])

        # Check if the destination file does not exist
        source_directory = os.path.dirname(source_module)
        # Define the new file path
        new_file_path = os.path.join(source_directory, filename + ".py")
        if not os.path.isfile(new_file_path):
            # Copy the source module to the new file path
            shutil.copy(source_module, new_file_path)            

        # Creates a new class in the new miner file for this specific miner
        copy_and_rename_class(new_file_path, "Miner", classname_instance)

        print("Serving Miner")
        command = f'pm2 start "python -m eden_subnet.miner.{filename} --key_name {module_name} --host 0.0.0.0 --port {next_port}" --name "{module_name}"'
        os.system(command)
        print("Miner served.")


def get_ss58_address(name):
    # Construct the path to the JSON file
    file_path = os.path.expanduser(f"~/.commune/key/{name}.json")

    try:
        # Open and read the JSON file
        with open(file_path, 'r') as file:
            data = json.load(file)

        # Extract the 'data' field and parse it as JSON
        data_json = json.loads(data['data'])

        # Return the 'ss58_address' field
        return data_json['ss58_address']

    except FileNotFoundError:
        print(f"No file found for {name}")
        return None
    except KeyError as e:
        print(f"Key error: {e} - Check JSON structure")
        return None
    except json.JSONDecodeError:
        print("Error decoding JSON")
        return None

def register(module_path, wan_ip, port, NumModules, Netuid):


    for i in range(NumModules):
        key = "module"
        module_name = f"{module_path}_{i}"
        next_port = port + i
        print("Port: ", next_port)
        print("Transfer Com to new miner key")
        subprocess.run(["comx", "balance", "transfer", key, "305", get_ss58_address(module_name)])
        sleep(10)

        print("Register new miner key")
        subprocess.run(["comx", "module", "register", "--ip", wan_ip, "--port", f"{next_port}", "--stake", "300", module_name, module_name, "--netuid", f"{Netuid}"])
        print(f"Registered {module_name} at {wan_ip}:{next_port}")
        sleep(10)

        print("Remove Temp Stake from new miner")
        subprocess.run(["comx", "balance", "unstake",  module_name, "250", get_ss58_address(module_name), "--netuid", f"{Netuid}"])
        print(f"Stake Removed")
        sleep(10)

        print("Send fund back from new miner")
        subprocess.run(["comx", "balance", "transfer",  module_name, "250", get_ss58_address("module")])
        print(f"Funds send")
        sleep(10)
            
        #print("Test call miner")
        # c call model.openrouter::cool2/generate hey
        #subprocess.run(["c", "call", module_name+"/generate", "hey"])
        #sleep(5)

        # Wait before repeating the registration process
        sleep(60)
        print("loop")


if __name__ == "__main__":
    source_miner="eden_subnet/miner/miner.py"
    source_validator="eden_subnet/validator/validator.py"
    module_path="aliens.alienware"
    source_module=source_miner
    wan_ip="72.220.238.205"
    port=25005
    NumModules=200
    Netuid=10

    serve_modules(module_path=module_path,source_module=source_miner,port=port, NumModules=NumModules, Netuid=Netuid)
    register(module_path=module_path,wan_ip=wan_ip,port=port, NumModules=NumModules, Netuid=Netuid)


    