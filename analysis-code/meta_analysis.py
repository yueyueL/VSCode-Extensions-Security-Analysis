import json
import os
import timeit

def analyze_package_json(package_json_path):
    """ Analyzes a package.json file. """

    with open(package_json_path, 'r') as package_json:
        package = json.load(package_json)

    commands, configurations = [], {}
    if 'contributes' in package:
        if 'commands' in package['contributes']:
            commands =  package['contributes']['commands']
        else:
            commands = []

        if 'configuration' in package['contributes']:
            if isinstance(package['contributes']['configuration'], list):
                for configuration in package['contributes']['configuration']:
                    if 'properties' in configuration:
                        for property in configuration['properties']:
                            configurations[property] = configuration['properties'][property]
            elif isinstance(package['contributes']['configuration'], dict):
                if 'properties' in package['contributes']['configuration']:
                    for property in package['contributes']['configuration']['properties']:
                        configurations[property] = package['contributes']['configuration']['properties'][property]

    return commands, configurations


def process_commands(commands_in_codes, commands_in_package_json):
    """ Processes the commands found in the package.json file. """

    output_commands = []
    for command in commands_in_package_json:
        output_command = {}

        command_name = command['command'].lower()
        if 'command' in command:
            output_command['command'] = command['command']
        if 'title' in command:
            output_command['title'] = command['title']

        for command_in_code in commands_in_codes:
            value, param = command_in_code['value'].lower(), ""
            output_command['RegisterInCode'] = False
            
            if command_name in value or command_name.split('.')[-1] in value or command_name.split('::')[-1] in value:
                output_command['RegisterInCode'] = True
                break
            
        output_commands.append(output_command)

    return output_commands

