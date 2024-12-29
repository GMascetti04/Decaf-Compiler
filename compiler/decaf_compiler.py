import sys
import decaf_parser
import decaf_irgen
import argparse
import os
import json


def modify_file_extension(file_name): 
    if file_name.endswith('.decaf'): 
        return file_name[:-6] + '.ami'
    return file_name + '.ami'

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description="A compiler for the programming language Decaf")
    
    parser.add_argument("--infile", type=str, help="input file - will read from stdin if none specified", required=True)
    parser.add_argument("--outdir", type=str, help='output directory')
    parser.add_argument("--save-builds", action="store_true", help="Save builds if this flag is set")

    args = parser.parse_args()
    
    with open(args.infile, 'r') as read_file:
        
        
    
        ast = decaf_parser.generate_ast(read_file.read())
    
        if ast == None:
            print("\033[31mCompilation Failed\033[0m", file=sys.stderr)
            sys.exit(1)
            
        build_directory = args.outdir if args.outdir else os.getcwd()
        
        os.makedirs(build_directory, exist_ok=True)
        
        
        gen = decaf_irgen.IRCodeGenerator(ast)
        program = gen.generate_code()
    
        program.create_basic_blocks()
        
        if args.save_builds:
            temp_dir = os.path.join(build_directory, 'build')
            os.makedirs(temp_dir, exist_ok=True)
            with open(os.path.join(temp_dir, "ast.json"), 'w') as astFile:
                astFile.write(json.dumps(ast.to_dict(), indent= 1))
            with open(os.path.join(temp_dir, "A3.tac"), 'w') as tacFile:
                program.print_to_file(tacFile)
        
        with open(os.path.join(build_directory,modify_file_extension(args.infile)), 'w') as outFile:
              outFile.write("TODO: convert IR to AMI")
    
        print(f'\033[32mCompilation Succeeded\033[0m', file=sys.stderr)