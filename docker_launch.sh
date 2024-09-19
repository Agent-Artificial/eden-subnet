#!/bin/bash

# MIT License - Copyright (c) 2023 Bakobiibizo (https://github.com/bakobiibizo)

set -e

# Utilty function
capitalize() {
    echo "$(tr '[:lower:]' '[:upper:]' <<< ${1:0:1})${1:1}"
}

# accepts env_file as a positional argument eg. bash docker_launch.sh .env
env_file=$1

# Check if .env file exists if not create it if it does ask if it should be overwritten
if [ -z "$env_file" ]; then
    env_file=".env"
fi
if [ ! -f "$env_file" ]; then
    touch "$env_file"
    # We have to set this to true so that the flag is set if the user does not hit the prompt to overwrite
    is_overwrite_env=true
else
    read -p "$env_file already exists. Do you want to overwrite it? [y/N] " overwrite
    if [[ "$overwrite" == "y" || "$overwrite" == "Y" ]]; then
        rm "$env_file"
        touch "$env_file"
        is_overwrite_env=true
    else
        echo "$env_file will be not overwritten"
        is_overwrite_env=false
    fi
fi

# Select validator or miner
while true; do
    read -p "Launch validator or miner?[v/M] " choice

    case $choice in
        v | V)
            echo "Launching validator"
            role="validator"
            break
            ;;
        m | M)
            echo "Launching miner"
            role="miner"
            break
            ;;
        *)
            echo "Invalid choice"
            ;;
    esac
done

# Check if docker-compose.yaml exists if not create it if it does then ask if it should be overwritten
if [ ! -f docker-compose.yaml ]; then
    cp docker-compose.template.yaml docker-compose.yaml
else
    read -p "docker-compose.yaml already exists. Do you want to overwrite it? [y/N] " overwrite
    if [[ "$overwrite" == "y" || "$overwrite" == "Y" ]]; then
        rm docker-compose.yaml
        cp docker-compose.template.yaml docker-compose.yaml
    else
        echo "docker-compose.yaml not overwritten"
        exit 1
    fi  
fi

# Function to prompt the user for environment variable values and writes those values to an environment file
prompt_for_input() {
    value_to_set=$1
    while true; do
        read -p "Please enter a value for $value_to_set: " user_input
        if [[ -n "$user_input" ]]; then
            if grep -q "$value_to_set=" "$env_file"; then
                sed -i "/$value_to_set=/d" "$env_file"
                echo "$value_to_set=$user_input" >> "$env_file"
                break
            else
                echo "$value_to_set=$user_input" >> "$env_file"
                break
            fi
        else
            echo "Invalid input. Please try again."
        fi
    done
    echo "Value set to $user_input for $value_to_set in $env_file"    
}

# Check if we should be overwriting the environment file if we are then prompt the user for input
if $is_overwrite_env; then
    for value in module_name key_name port host subnet_id cuda_device; do
        prompt_for_input "$value"
    done
fi

# Source the environment file 
source "$env_file"

container_name="$(echo "${module_name,,}")"



sed -i "s|CONTAINER_NAME|$container_name|g" docker-compose.yaml
sed -i "s|MODULE_NAME|$module_name|g" docker-compose.yaml
sed -i "s|KEY_NAME|$key_name|g" docker-compose.yaml
sed -i "s|PORT|$port|g" docker-compose.yaml
sed -i "s|HOST|$host|g" docker-compose.yaml
sed -i "s|SUBNET_ID|$subnet_id|g" docker-compose.yaml
sed -i "s|CUDA_DEVICE|$cuda_device|g" docker-compose.yaml

setup_role() {
    local role=$1
    local module_path="eden_subnet/$role/$(echo "$module_name" |  sed 's/\./_/g').py"

    module_path_dots=$(echo "$module_path" | sed 's/\//./g')
    sed -i "s|MODULE_PATH|$module_path_dots|g" docker-compose.yaml
    
    if [ ! -f "$module_path" ]; then
        cp "eden_subnet/$role/eden.py" "$module_path"
    fi
    
    for i in {0..8}; do
        if grep -q "|$(capitalize $role)_$i|" "$module_path"; then
            sed -i "s|$(capitalize $role)_$i|$key_name|g" "$module_path"
        fi
    done
}

setup_role "$role"

register() {
    modulename=$1
    keyname=$2
    module_port=$3
    module_host=$4
    netuid=$5

    comx module register "$modulename" "$keyname" "$netuid" 
}

create_key() {
    keyname=$1

    comx key create $keyname
}

transfer_balance() {
    keyname=$1
    read -p "Enter the amount to transfer: " amount
    read -p "Source key name: " source_key

    comx balance transfer $source_key $amount $keyname
}

read -p "Do you want to create a new key? [y/N] " create_new_key

if [[ "$create_new_key" == "y" || "$create_new_key" == "Y" ]]; then
    create_key "$key_name"
fi

read -p "Do you want to transfer a balance to the key? [y/N] " transfer_balance
if [[ "$transfer_balance" == "y" || "$transfer_balance" == "Y" ]]; then
    transfer_balance "$key_name"
fi

read -p "Do you want to register the module? [y/N] " register_module

if [[ "$register_module" == "y" || "$register_module" == "Y" ]]; then
    register "$module_name" "$key_name" "$port" "$host" "$subnet_id"
fi

docker compose up -d --remove-orphans

