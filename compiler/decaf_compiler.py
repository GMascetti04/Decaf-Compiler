import sys
import decaf_lexer
import decaf_parser
import decaf_codegen
import argparse

def modify_file_extension(file_name): 
    if file_name.endswith('.decaf'): 
        return file_name[:-6] + '.ami'
    return file_name + '.ami'

def compile(infile, outfile):
        
    data = infile.read()
    
    ast = decaf_parser.parse_file(data)
    
    if ast == None:
        print("\033[31mCompilation Failed\033[0m", file=sys.stderr)
        sys.exit(1)
        
    gen = decaf_codegen.AbstractCodeGenerator(ast)
    program = gen.generate_code()
        
    program.print_to_file(outfile)
    

    print(f'\033[32mCompilation Succeeded\033[0m', file=sys.stderr)

    





if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description="A compiler for the programming language Decaf")
    
    parser.add_argument("--infile", type=str, help="input file - will read from stdin if none specified")
    
    
    
    
    args = parser.parse_args()
    
    if args.infile == None:
        compile(sys.stdin, sys.stdout)
    else:
        try:
            read_file = open(args.infile, 'r')
            out_file = open(modify_file_extension(args.infile), 'w')
            compile(read_file, out_file)

            
        except Exception:
           print("Could not open file")
    
   
            