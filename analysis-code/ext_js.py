import logging
import json
import danger_analysis
from get_pdg import get_node_computed_value_e, get_node_value_e
import timeit
import os
import pdg_js.utility_df as utility_df
import utility
import get_pdg
import pdg_js.node as _node
import re
from meta_analysis import analyze_package_json


PRINT_DEBUG = utility.PRINT_DEBUG

def load_sensitive_apis(sensitive_apis_path, extension_path, benchmarks):
    """ Loads the sensitive APIs to consider from the sensitive_apis_path JSON file. """

    if sensitive_apis_path is None or not os.path.isfile(sensitive_apis_path):
        # Should not happen, but just in case
        logging.critical('%s is not a valid path. No sensitive APIs can be considered. The '
                         'extension %s cannot be analyzed', sensitive_apis_path, extension_path)
        benchmarks['crashes'].append('no-valid-api-file')
        return None

    with open(sensitive_apis_path) as json_data:
        try:
            return json.loads(json_data.read())
        except json.decoder.JSONDecodeError:  # Should not happen, but just in case
            logging.critical('Something went wrong to open %s', sensitive_apis_path)

    logging.critical('No sensitive APIs can be considered. '
                     'The extension %s cannot be analyzed', extension_path)
    benchmarks['crashes'].append('no-api-considered')
    return None



def default(o):
    """ Because of TypeError: Object of type ValueExpr is not JSON serializable.
    Conversion of such objects into str. """
    if isinstance(o, (_node.ValueExpr, _node.FunctionExpression)):
        parent = o.parent
        while True:
            if parent.parent:
                parent = parent.parent
            else:
                break
        if "filename" in parent.attributes:
            filename = parent.attributes["filename"]
            raw_code = open(filename, 'rb').read()[o.attributes['range'][0]:
                                                   o.attributes['range'][1]]
            return re.sub(' {2,}', ' ', raw_code.decode("utf8", "ignore"))

    if type(o).__name__ == '_iterencode':  # Replace with the type causing issue
        return str(o) 

    return str(o)


def look_for_vulnerabilities(node, whoami, sinks, dangers):
    """ Analysis of a PDG to detect dangerous sinks, stored in dangers. """

    for child in node.children:
        if child.name in ('CallExpression', 'TaggedTemplateExpression'):
            if len(child.children) > 0 and child.children[0].body in ('callee', 'tag'):
                callee = child.children[0]
                call_expr_value = get_node_computed_value_e(callee)
                call_expr_value_all = get_node_computed_value_e(child)
                child.set_value(call_expr_value_all)
                if isinstance(call_expr_value, str):  # No need to check if it is not a str
                    flagged_sink, sink = danger_analysis.check_dangerous_sinks(child,
                                                                               call_expr_value,
                                                                               sinks)
                    if flagged_sink:  # Dangerous sink used
                        danger_analysis.add_danger(where=dangers, api_name=sink, api_node=child,
                                                   api_value=call_expr_value_all,
                                                   params=child.children[1:])

                elif isinstance(call_expr_value_all, str):  # Special case for asynchronous XHR
                    # {'XMLHttpRequest()': {}, 'onreadystatechange': <node.FunctionExpr}.open(...)
                    flagged_xhr, sink = danger_analysis.check_async_xhr(child, call_expr_value_all,
                                                                        sinks)
                    if flagged_xhr:  # Dangerous sink used
                        danger_analysis.add_danger(where=dangers, api_name=sink, api_node=child,
                                                   api_value=call_expr_value_all,
                                                   params=child.children[1:])

        look_for_vulnerabilities(child, whoami=whoami, sinks=sinks, dangers=dangers)

def check_is_vulnerable_function(node, whoami, sinks, dangers):
    for child in node.children:
        if child.name in ('CallExpression', 'TaggedTemplateExpression'):
            if len(child.children) > 0 and child.children[0].body in ('callee', 'tag'):
                callee = child.children[0]
                call_expr_value = get_node_computed_value_e(callee)
                call_expr_value_all = get_node_computed_value_e(child)
                child.set_value(call_expr_value_all)
                if isinstance(call_expr_value, str):
                    flagged_sink, sink = danger_analysis.check_dangerous_sinks(child,
                                                                               call_expr_value,
                                                                               sinks)
                    if flagged_sink:
                        return True
                elif isinstance(call_expr_value_all, str):
                    flagged_xhr, sink = danger_analysis.check_async_xhr(child, call_expr_value_all,
                                                                        sinks)
                    if flagged_xhr:
                        return True
        # Recursive call to check each child node
        if check_is_vulnerable_function(child, whoami, sinks, dangers):
            return True

    return False



def analyze_extension_part(pdg, whoami, extension_part, benchmarks):

    start = timeit.default_timer()

    sources = extension_part.sources  # Sources that should be looked for
    dirties = extension_part.dirties  

    # Fills dangers.direct = directly executable sinks
    look_for_vulnerabilities(pdg, whoami=whoami, sinks=sources, dangers=dirties)

    benchmarks[whoami + ': dangers'] = timeit.default_timer() - start
    utility_df.micro_benchmark('Successfully collected the dangers and elements in the '
                               + whoami + ' in', timeit.default_timer() - start)
    



def fill_vulnerability_dict(my_dict, wa, wa_node, where):
    """ Fills the dictionary my_dict containing the vulnerability results. """

    my_dict['api'] = wa  # API to communicate with the web app
    my_dict['line'] = wa_node.get_line()  # Line where the previous API was detected
    my_dict['filename'] = wa_node.get_file()  # Corresponding file (CS vs. BP)
    my_dict['where'] = where  # Context, value of the node leading to the vulnerability




def get_target_node_from_cfgs(cfgs, extension_part, whoami):
    """ Gets the target node from the CFGs. """
    sources = extension_part.sources  # Sources that should be looked for
    targets = extension_part.target_nodes  
    get_target_ArrowFunctionExpression(cfgs, whoami, sources, targets)
    # look_for_vulnerabilities(cfgs, whoami=whoami, sinks=sources, dangers=targets)

def get_target_ArrowFunctionExpression(node, whoami, sources, targets, layer=0):
    if layer > 10:
        return
    
    for child in node.children:        
        if child.name in ('Property'):
            if len(child.children) > 0:
                for sub_child in child.children:
                    if sub_child.name == "ArrowFunctionExpression":
                        is_vulnerable_function = check_is_vulnerable_function(sub_child, whoami=whoami, sinks=sources, dangers=targets)
                        
                        if is_vulnerable_function:
                            danger_analysis.add_danger(where=targets, api_name="func", api_node=child,
                                                                            api_value=None,
                                                                            params=None)
        get_target_ArrowFunctionExpression(child, whoami, sources, targets, layer + 1)




def pdg_test_analysis(cs_path, store_json_p = None, sink_source_path = None, Prune_Analysis = False):
    utility_df.limit_memory(20 * 10 ** 9)  # Limiting the memory usage to 20GB
    res_dict = dict()    
    extension_path = res_dict['extension'] = os.path.dirname(cs_path)
    print(extension_path)

    if os.path.exists(extension_path + '/analysis/analysis.json'):
        return

    benchmarks = res_dict['benchmarks'] = dict()
    res_dict['tool_version'] = "v3"
    manifest_path = os.path.join(extension_path, 'package.json')
    
    try:
        utility.print_info('> PDG of ' + cs_path)
        sensitive_apis = load_sensitive_apis(sink_source_path, extension_path, benchmarks=benchmarks)
        extension = danger_analysis.Extension(apis = sensitive_apis)
        vsix = extension.vsix

        if Prune_Analysis:
            graph_type, pdg = get_pdg.get_pdg(file_path=cs_path, res_dict=benchmarks, CFG_only = True)  # Builds CS PDG
        else:
            graph_type, pdg = get_pdg.get_pdg(file_path=cs_path, res_dict=benchmarks)  # Builds CS PDG
        update_benchmarks_pdg(benchmarks=benchmarks, whoami='Asix') 

        if graph_type == 'CFG':   
            get_target_node_from_cfgs(pdg, vsix, whoami='vsix')
            target_nodes = vsix.target_nodes
            print("target_nodes", len(target_nodes))
            for target_node in target_nodes:
                pruned_cfgs = target_node.api_node
                return_graph_type, pdg = get_pdg.get_pdg_based_on_pruned_cfg(pruned_cfgs)
                analyze_extension_part(pdg, whoami='vsix', extension_part=vsix,
                    benchmarks=benchmarks)  
            update_sources(whoami='vsix', res_dict=res_dict, sources = vsix.sources, dirties=vsix.dirties, manifest_path= manifest_path, benchmarks=benchmarks, cs_path=cs_path)
                
            
        elif graph_type == 'DFG':
            with utility_df.Timeout(600):
                utility.print_info('---\nIn the VSIX:')
                analyze_extension_part(pdg, whoami='vsix', extension_part=vsix,
                                    benchmarks=benchmarks)        

                if utility.TEST:  # For the automated checks
                    return
                update_sources(whoami='vsix', res_dict=res_dict, sources = vsix.sources, dirties=vsix.dirties, manifest_path= manifest_path, benchmarks=benchmarks, cs_path=cs_path)

    except utility_df.Timeout.Timeout:
        logging.exception('Analyzing the extension timed out for %s', cs_path)
        if 'crashes' not in benchmarks:
            benchmarks['crashes'] = []
        benchmarks['crashes'].append('extension-analysis-timeout')

    if PRINT_DEBUG:
        print(json.dumps(res_dict, indent=4, sort_keys=False, default=default, skipkeys=True))
        #print(json.dumps(messages_dict, indent=4, sort_keys=False, default=default, skipkeys=True))
    else:
        store_analysis_results(extension_path, store_json_p, res_dict)
        print('Analysis results stored in ' + extension_path + '/analysis/analysis.json')


def check_based_json_dict(res_dict):
    """ Check if the extension is vulnerable based on the analysis result. """

    if "vsix" in res_dict.keys():
        for source in res_dict["vsix"].keys():
            if source != "RequestedConfiguration" and source != "RequestedCommands":
                for danger in res_dict["vsix"][source]:
                    for key in danger.keys():
                        if isinstance(danger[key], dict):
                            for sub_key in danger[key].keys():
                                if isinstance(danger[key][sub_key], dict):
                                    print("Error: ", danger[key][sub_key])
                                    danger[key][sub_key] = str(danger[key][sub_key])

def store_analysis_results(extension_path, json_analysis, res_dict):
    """ Stores the analysis results: res_dict in json_analysis and messages_dict in json_messages,
    for the extension in extension_path. """

    if json_analysis is None:
        store_dir = os.path.join(extension_path, 'analysis/')
        if not os.path.exists(store_dir):
            os.makedirs(store_dir)
        json_analysis = os.path.join(store_dir, 'analysis.json')
    # print(res_dict)
    check_based_json_dict(res_dict)
    with open(json_analysis, 'w') as json_data:
        json.dump(res_dict, json_data, indent=4, sort_keys=False, default=default,
                  skipkeys=True)



def update_sources(whoami, res_dict, sources,dirties,manifest_path, benchmarks,cs_path):
    start = timeit.default_timer()
    res_dict[whoami] = dict()

    data_dict = res_dict[whoami]
    for source in sources:
        res_dict[whoami][source] = []
        

    for danger in dirties:
        logging.debug('Analyzing the dangerous API %s', danger.api_name)
        api_name = danger.api_name
        
        dangers_id_dict = dict()
        dangers_id_dict['danger'] = danger.api_name  # Dangerous sink
        dangers_id_dict['value'] = danger.api_value  # Corresponding value
        dangers_id_dict['line'] = danger.api_node.get_line()  # Corresponding line    

        if isinstance(danger.api_params, list):
            for danger_nb, _ in enumerate(danger.api_params):
                sink_param_value = get_node_computed_value_e(danger.api_params[danger_nb])
                dangers_id_dict['sink-param' + str(danger_nb + 1)] = sink_param_value  # Param

        for source in sources:
            if danger.api_name in sources[source]:
                if source == "InputBox":
                    ## add complete line code
                    with open(cs_path, "r") as f:
                        content = f.readlines()
                    
                    line_str = danger.api_node.get_line()
                    line_start = line_str.split(" - ")[0]
                    line_end = line_str.split(" - ")[1]
                    line_code = ""
                    for i in range(int(line_start), int(line_end) + 1):
                        line_code += content[i - 1]
                    dangers_id_dict['code'] = line_code

                data_dict[source].append(dangers_id_dict)

    commands, configurations = analyze_package_json(manifest_path)
    data_dict["RequestedConfiguration"] = configurations
    data_dict["RequestedCommands"] = commands
    
    benchmarks[whoami + ': got sources'] = timeit.default_timer() - start




def update_benchmarks_pdg(benchmarks, whoami):
    """ PDG generation benchmarks are generic, here we make the difference between CS and BP. """

    if 'errors' in benchmarks:
        if 'crashes' not in benchmarks:
            benchmarks['crashes'] = []
        crashes = benchmarks.pop('errors')
        for el in crashes:
            benchmarks['crashes'].append(whoami + ': ' + el)
    if 'got AST' in benchmarks:
        benchmarks[whoami + ': got AST'] = benchmarks.pop('got AST')
    if 'AST' in benchmarks:
        benchmarks[whoami + ': AST'] = benchmarks.pop('AST')
    if 'CFG' in benchmarks:
        benchmarks[whoami + ': CFG'] = benchmarks.pop('CFG')
    if 'PDG' in benchmarks:
        benchmarks[whoami + ': PDG'] = benchmarks.pop('PDG')



def print_node(node):
    if isinstance(node, _node.Value):
        if "name" in node.attributes.keys():
            print("-", node.name, node.value, node.attributes["name"],node.attributes)
        else:
            print("--", node.name, node.value,  node.attributes)
    else:
        print("====>", node.name,  node.attributes)
    # for child in node.children:
    #     print_node(child)
