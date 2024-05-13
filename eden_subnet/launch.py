import subprocess

module_name = "eden.Validator_"

i = 2
# subprocess.run(
#    [
#        "comx",
#        "module",
#        "register",
#        "--netuid",
#        "10",
#        f"{module_name}{i}",
#        f"{module_name}{i}",
#    ],
#    check=True,
# )
subprocess.run(
    [
        "comx",
        "module",
        "update",
        "--netuid",
        "10",
        f"{module_name}{i}",
        f"{module_name}{i}",
        "24.66.238.82",
        f"100{i}0",
    ],
    check=True,
)
