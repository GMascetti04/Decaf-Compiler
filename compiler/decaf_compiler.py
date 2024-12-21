import sys
import decaf_lexer
import decaf_parser
import decaf_codegen

def modify_file_extension(file_name): 
    if file_name.endswith('.decaf'): 
        return file_name[:-6] + '.ami'
    return file_name + '.ami'

def main():
    if len(sys.argv) < 2:
        print("\033[31mError: No input file specified\033[0m")
        return
    
    try:
        file = open(sys.argv[1], 'r', encoding="utf-8")
        data = file.read()
        
        ast = decaf_parser.parse_file(data)
        
        if ast == None:
            print("\033[31mCompilation Failed\033[0m")
            sys.exit(1)
            
        elif len(sys.argv) >= 3 and sys.argv[2] == '--show-ast':
            print(ast)
            
        print(ast)
        
        gen = decaf_codegen.AbstractCodeGenerator(ast)
        program = gen.generate_code()
        
        

        output_file_name = modify_file_extension(sys.argv[1])

        with open(output_file_name, 'w') as file:
            program.print_to_file(file)
        

        print(f'\033[32mCompilation Succeeded - Program written to "{output_file_name}".\033[0m (Run with "--show-ast" to print AST)')

    except OSError:
        print("Could not open file")



if __name__ == "__main__":
   main()
    