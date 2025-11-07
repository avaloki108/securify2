import argparse
from pathlib import Path
from securify.analyses.analysis import discover_patterns, AnalysisContext, AnalysisConfiguration, print_pattern_matches
from securify.solidity import solidity_ast_compiler, solidity_cfg_compiler
from securify.staticanalysis import static_analysis
from securify.staticanalysis.factencoder import encode
from securify.staticanalysis.visualization import visualize
from securify.utils.ethereum_blockchain import get_contract_from_blockchain
from securify.utils.truffle_integration import is_truffle_project, get_truffle_project_root, TruffleProject
import re
import semantic_version
from securify.solidity.solidity_ast_compiler import  compiler_version
import sys
import os

def get_list_of_patterns(context=AnalysisContext(), patterns='all', exclude_patterns=[], severity_inc=[], severity_exc=[]):
    pattern_classes = discover_patterns()

    use_patterns = list(map(lambda p: p(context), pattern_classes))

    if patterns != 'all':
        # Comply with vulnerability table: add pattern suffix to every pattern name
        patterns = list(map(lambda x: x + "Pattern", patterns))
        use_patterns = list(filter(lambda p: p.__class__.__name__ in patterns, use_patterns))

    extended_exclude_patterns = list(map(lambda x: x + "Pattern", exclude_patterns))
    use_patterns = list(filter(lambda p: p.__class__.__name__ not in extended_exclude_patterns, use_patterns))

    if severity_inc != []:
        use_patterns = list(filter(lambda p: p.severity.name in severity_inc, use_patterns))

    if severity_exc != []:
        use_patterns = list(filter(lambda p: p.severity.name not in severity_exc, use_patterns))

    return use_patterns


class ListPatterns(argparse.Action):
    def __call__(self, parser, *args, **kwargs):
        patterns = get_list_of_patterns()
        for p in patterns:
            # Comply with vulnerability table: remove 'Pattern' suffix
            print("Name:", p.__class__.__name__.replace('Pattern', ''))
            print("Severity:", p.severity.name)
            msg = "Description: " + p.description
            print(msg)
            print(len(msg) * "-")

        parser.exit()


def normalize_severity_args(args):
    translate = dict(C='CRITICAL', H='HIGH', M='MEDIUM', L='LOW', O='OPTIMIZATION', I='INFO')

    if args == 'all':
        return translate.values()

    if args == 'none':
        return []

    severities = args.split(',')
    severities = [s.strip().upper() for s in severities]

    def expand_severity(s):

        if len(s) > 1:
            return s
        else:
            return translate[s]

    severities = [expand_severity(s) for s in severities]
    return severities


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='securify2.5: A static analyzer for Ethereum contracts.',
        usage="securify contract.sol [opts]")

    parser.add_argument('contract',
                        help='A contract to analyze. Can be a .sol file, a Truffle project directory, or an address of a contract on blockchain')

    parser.add_argument("--ignore-pragma", help="By default securify2.5 changes the pragma directives in contracts with pragma \
                                                directives <= 0.5.8. Use this flag to ignore this functionality",
                                                action='store_true')

    parser.add_argument("--solidity", help="Define path to solidity binary", default=None)

    parser.add_argument("--stack-limit",
                        help="Set python stack maximum depth. This might be useful since some contracts might exceed this limit.",
                        type=int,
                        default=1000)

    pattern_group = parser.add_argument_group('Patterns')

    pattern_group.add_argument("--list-patterns", "-l", help="List the available patterns to check",
                               nargs=0,
                               action=ListPatterns)

    pattern_group.add_argument("--use-patterns", "-p",
                               help="Pattern names separated with spaces to include in the analysis, default='all'",
                               action="store",
                               nargs='+',
                               dest='use_patterns', default='all')

    pattern_group.add_argument("--exclude-patterns",
                               help="Pattern names separated with spaces to exclude from the analysis",
                               action="store",
                               nargs='+',
                               dest='exclude_patterns', default=[])

    pattern_group.add_argument("--include-severity", "-i",
                               help="Severity levels to include: \
                               CRITICAL, HIGH, MEDIUM, LOW, INFO",
                               action='store',
                               nargs='+',
                               dest='include_severity', default=[])

    pattern_group.add_argument("--exclude-severity", "-e",
                               help="Severity levels to exclude: \
                               CRITICAL, HIGH, MEDIUM, LOW, INFO",
                               action='store',
                               nargs='+',
                               dest='exclude_severity', default=[])

    pattern_group.add_argument("--include-contracts", "-c",
                               help="Contracts to include in the output",
                               action='store',
                               nargs='+',
                               default='all')

    pattern_group.add_argument("--exclude-contracts",
                               help="Contracts to exclude from the output",
                               action='store',
                               nargs='+',
                               default=[])

    pattern_group.add_argument("--show-compliants",
                               help="Show compliant matches. Useful for debugging.",
                               action='store_true',
                               default=False)

    parser.add_argument('--visualize', '-v', help='Visualize AST', action='store_true')


    truffle_group = parser.add_argument_group('Truffle Integration')

    truffle_group.add_argument('--truffle-project', '-t',
                               help="Analyze all contracts in a Truffle project.",
                               action='store_true')
    
    truffle_group.add_argument('--contract-name',
                               help="For Truffle projects, specify which contract to analyze (default: analyze all).",
                               default=None)


    etherscan_group = parser.add_argument_group('Etherscan API')

    etherscan_group.add_argument('--from-blockchain', '-b',
                                 help="The address of a contract in the Ethereum blockchain.",
                                 action='store_true')
    etherscan_group.add_argument('--key', '-k', help="The file where the api-key for etherscan.io is stored.",
                                 default='api_key.txt')


    compilation_group = parser.add_argument_group('Compilation of Datalog code')

    compilation_group.add_argument('--interpreter',
                                   help="Use the souffle interpreter to run the datalog code.\
                                        Particularly useful when experimenting with new patterns.",
                                   action='store_true')

    compilation_group.add_argument('--recompile', help="Force recompilation of the datalog code.",
                                   action='store_true')

    base_path = Path(__file__).parent
    compilation_group.add_argument('--library-dir', help="Directory of the functors' library.",
                                   default=base_path / 'staticanalysis/libfunctors/')

    args = parser.parse_args()
    return args

def prepare_env(binary=None):
    import os

    base_path = Path(__file__).parent / 'staticanalysis/libfunctors/'
    def check_for_libfunctors():

        libfunctors = base_path / 'libfunctors.so'
        compile_script = './compile_functors.sh'
        if libfunctors.is_file(): return
        print("libfunctors.so not compiled. Compiling it now...")
        os.system("cd " + base_path.absolute().as_posix() + " && " + compile_script + "&& cd - > /dev/null")

    def check_LD_LIBRARY_PATH():
        base = base_path.absolute().as_posix()
        current = os.environ.get('LD_LIBRARY_PATH', '')
        if current:
            if base in current.split(':'):
                return
            print("Adding libfunctors to LD_LIBRARY_PATH...")
            os.environ['LD_LIBRARY_PATH'] = current + ':' + base
        else:
            print("Environment variable LD_LIBRARY_PATH not set. Setting it up...")
            os.environ['LD_LIBRARY_PATH'] = base

    def define_SOLC_BINARY(binary=None):
        if binary is None: return
        print("Setting SOLC_BINARY to {}...".format(binary))
        os.environ['SOLC_BINARY'] = binary

    check_for_libfunctors()
    check_LD_LIBRARY_PATH()
    define_SOLC_BINARY(binary)
    return

# Reads the current contract and creates a new one with the pragma directive fixed
def fix_pragma(contract):

    installed_version = compiler_version()

    fixed_pragma_file = "/tmp/fixed_pragma.sol"

    rpattern = r"pragma solidity \^?(\d*\.\d*\.\d*);?"

    with open(contract) as c:
        source = c.read()

    pattern = re.compile(rpattern)

    try :
        match = pattern.search(source)
        solidity_version = match.group(1)
    except:
        return contract

    installed_version = ".".join([str(installed_version.major), str(installed_version.minor), str(installed_version.patch)])

    if semantic_version.Version(solidity_version) >= semantic_version.Version(installed_version):
        return contract

    print("pragma directive defines a prior version to {v}. Changing pragma version to {v}....".format(v=installed_version))

    new_source = re.sub(rpattern, r"pragma solidity {};".format(installed_version), source)

    with open(fixed_pragma_file, 'w') as f:
        f.write(new_source)

    return fixed_pragma_file


def analyze_contract(contract_path, args, souffle_config):
    """
    Analyze a single contract file
    
    Args:
        contract_path: Path to the contract file
        args: Command-line arguments
        souffle_config: Configuration for Souffle
        
    Returns:
        List of pattern matches
    """
    if not args.ignore_pragma:
        contract_path = fix_pragma(contract_path)
    
    config = AnalysisConfiguration(
        ast_compiler=lambda t: solidity_ast_compiler.compile_ast(t.source_file),
        cfg_compiler=lambda t: solidity_cfg_compiler.compile_cfg(t.ast).cfg,
        static_analysis=lambda t: static_analysis.analyze_cfg(t.cfg, **souffle_config),
    )
    
    context = AnalysisContext(
        config=config,
        source_file=contract_path
    )
    
    if args.visualize:
        cfg = context.cfg
        facts, _ = encode(cfg)
        visualize(facts).render("out/dl", format="svg", cleanup=True)
    
    patterns = get_list_of_patterns(
        context=context,
        patterns=args.use_patterns,
        exclude_patterns=args.exclude_patterns,
        severity_inc=args.include_severity,
        severity_exc=args.exclude_severity
    )
    
    matches = []
    for pattern in patterns:
        matches.extend(pattern.find_matches())
    
    skip_compliant = not args.show_compliants
    print_pattern_matches(
        context, matches, skip_compliant=skip_compliant,
        include_contracts=args.include_contracts,
        exclude_contracts=args.exclude_contracts
    )
    
    return matches


def handle_truffle_project(project_path, args, souffle_config):
    """
    Handle analysis of a Truffle project
    
    Args:
        project_path: Path to the Truffle project
        args: Command-line arguments
        souffle_config: Configuration for Souffle
    """
    try:
        project = TruffleProject(project_path)
        print(f"Detected Truffle project at: {project.project_path}")
        
        contracts = project.list_contracts()
        
        if not contracts:
            print("No contracts found in the Truffle project.")
            return
        
        # Filter by contract name if specified
        if args.contract_name:
            contracts = [c for c in contracts if c.stem == args.contract_name]
            if not contracts:
                print(f"Contract '{args.contract_name}' not found in the project.")
                return
        
        print(f"Found {len(contracts)} contract(s) to analyze.")
        
        # Analyze each contract
        for contract_file in contracts:
            print(f"\n{'='*80}")
            print(f"Analyzing: {contract_file.name}")
            print(f"{'='*80}\n")
            
            try:
                # Flatten the contract to handle imports
                flattened_contract = project.flatten_contract(contract_file)
                
                # Analyze the flattened contract
                analyze_contract(flattened_contract, args, souffle_config)
                
                # Clean up temporary flattened file
                if flattened_contract != str(contract_file):
                    try:
                        os.unlink(flattened_contract)
                    except (OSError, FileNotFoundError):
                        # Ignore errors when cleaning up temp files
                        pass
                        
            except Exception as e:
                print(f"Error analyzing {contract_file.name}: {str(e)}")
                continue
    
    except Exception as e:
        print(f"Error processing Truffle project: {str(e)}")
        sys.exit(1)


def main():


    args = parse_arguments()

    prepare_env(binary=args.solidity)

    sys.setrecursionlimit(args.stack_limit)

    contract = args.contract

    if args.from_blockchain:
        contract = get_contract_from_blockchain(args.contract, args.key)

    souffle_config = dict(use_interpreter=args.interpreter, force_recompilation=args.recompile,
                          library_dir=args.library_dir)

    # Check if input is a Truffle project
    is_truffle = args.truffle_project or is_truffle_project(contract)
    
    if is_truffle:
        # Handle Truffle project
        project_path = contract if os.path.isdir(contract) else get_truffle_project_root(contract)
        if project_path:
            handle_truffle_project(project_path, args, souffle_config)
        else:
            print("Could not find Truffle project. Make sure truffle-config.js or truffle.js exists.")
            sys.exit(1)
    else:
        # Handle single contract file (original behavior)
        if not args.ignore_pragma:
            contract = fix_pragma(contract)

        config = AnalysisConfiguration(
            # TODO: this returns only the dict ast, but should return the object representation
            ast_compiler=lambda t: solidity_ast_compiler.compile_ast(t.source_file),
            cfg_compiler=lambda t: solidity_cfg_compiler.compile_cfg(t.ast).cfg,
            static_analysis=lambda t: static_analysis.analyze_cfg(t.cfg, **souffle_config),
        )

        context = AnalysisContext(
            config=config,
            source_file=contract
        )

        if args.visualize:
            cfg = context.cfg
            facts, _ = encode(cfg)
            visualize(facts).render("out/dl", format="svg", cleanup=True)

        patterns = get_list_of_patterns(context=context,
                                        patterns=args.use_patterns,
                                        exclude_patterns=args.exclude_patterns,
                                        severity_inc=args.include_severity,
                                        severity_exc=args.exclude_severity)

        matches = []

        for pattern in patterns:
            matches.extend(pattern.find_matches())

        skip_compliant = not args.show_compliants
        print_pattern_matches(context, matches, skip_compliant=skip_compliant,
                              include_contracts=args.include_contracts,
                              exclude_contracts=args.exclude_contracts)


if __name__ == '__main__':
    main()
