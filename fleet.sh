#!/bin/bash

# MIT License - Copyright (c) 2023 Bakobiibizo (https://github.com/bakobiibizo)

set -e

register() {
    module_path="$1"
    key_name="$1"
    host="$2"
    port="$3"
    netuid="$4"
    stake="$5"

    echo "Registering"
    comx module register "$key_name" "$key_name" --ip "$host" --port "$port" --netuid "$netuid" --stake "$stake"
    echo "Registered (hopefully)"

    echo "Serving"
    #pm2 start "python $module_path --key_name $key_name --host 0.0.0.0 --port $port" -n "$key_name" &
    echo "Served (hopefully)"
}
HOSTS=("146.190.145.119" "143.110.235.13" "24.144.87.254" "164.90.145.144" "137.184.12.184" "194.247.182.12" "104.167.17.5" "64.23.243.90" "143.198.54.46")
PORTS=("8000" "8000" "8002" "8001" "8004" "8007" "31698" "8003" "8003")
NAMES=("mcompass::miner1" "mcompass::miner3" "boden5" "mine6" "modri4" "epi9" "wunder4" "trump5")

for ((i = 0; i < ${#HOSTS[@]}; i++)); do
    PORT=${PORTS[i]}
    HOST=${HOSTS[i]}

    NETUID="17" # Replace with your actual netuid
    STAKE="10"  # Replace with your actual stake
    MOD="25"
    TRANSFER=$((STAKE + MOD))
    FILENAME="holding"
    CLASSNAME=${NAMES[i]}
    TRANSFERFROM=mods

    source_miner="eden_subnet/miner/eden.py"

    for i in {1..2}; do
        NAME="$FILENAME.$CLASSNAME$i"
        j=$((i + 1))
        echo "Checking file path"
        # Create the miner module if it doesn't exist
        if [ ! -f "eden_subnet/miner/$FILENAME.py" ]; then

            # Copy the source miner file to the destination
            destination_file="eden_subnet/miner/$FILENAME.py"
            cp "$source_miner" "$destination_file"
            # Replace the class name in the destination file
            sed -i "s/Miner_$j/$CLASSNAME/g" "$destination_file"
            echo "Miner module created at eden_subnet/miner/$FILENAME.py"

            module_path="eden_subnet/miner/$FILENAME.py"

        fi

        if [ ! -f "$HOME/.commune/key/$NAME.json" ]; then
            comx key create "$NAME"
        fi
        echo ""
        transfer_balance=$TRANSFER
        transfer_from=$TRANSFERFROM
        if [ "$transfer_balance" = "y" ]; then
            transfer_balance
        fi
        echo ""

        comx balance transfer "$transfer_from" "$transfer_balance" "$NAME"
        echo "Transfer of $transfer_from from $transfer_from to $NAME initiated."

        register "$NAME" "$HOST" "$PORT" "$NETUID" "$STAKE"
    done
done
