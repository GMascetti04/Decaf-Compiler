# Decaf-Compiler

This project is a compiler implemented in  [PLY (Python Lex-Yacc)](https://github.com/dabeaz/ply) for the language Decaf. It was initially created by Giovanni Mascetti for CSE 304: Compiler Design at Stony Brook University.


## Compiling Decaf Programs

To compile a Decaf program, run the following command

```sh
python3 decaf_compiler.py decaf-program.decaf
```

## Example Program

Below is an example program that calculates the sum of the numbers 1 and 2 and prints it to the console.

```java
class Example {

    public static void main() {
        int a, b, c;

        a = 1;
        b = 2;

        c = a + b;

        Out.print(c);
    }

}
```

## Abstract Register Machine Code

```asm
.static_data 0

#====== Code for class Out
M_print_1:
iwrite a0                                         
ret                                               
#====== Code for class Example
.start:
M_main_2:
move_immed_f t3, 1
move t0, t3
move_immed_f t4, 2
move t1, t4
iadd t5, t0, t1
move t2, t5
save t0 
save t1
save t2
save t3
save t4
save t5
move a0, t2
call M_print_1
move t6, a0
restore t5
restore t4
restore t3
restore t2
restore t1
restore t0
ret
```
