grammar cminus;

/*
 * ==========================================================
 * Regras léxicas
 * ==========================================================
 * O lexer transforma caracteres do arquivo .cminus em tokens.
 */

// Palavras reservadas
ELSE   : 'else' ;
IF     : 'if' ;
INT    : 'int' ;
RETURN : 'return' ;
VOID   : 'void' ;
WHILE  : 'while' ;

// Operadores relacionais
LET : '<=' ;
GET : '>=' ;
EQ  : '==' ;
NEQ : '!=' ;
LT  : '<' ;
GT  : '>' ;

// Atribuição
ASSIGN : '=' ;

// Operadores aritméticos
PLUS  : '+' ;
MINUS : '-' ;
TIMES : '*' ;
OVER  : '/' ;

// Símbolos
LPAREN  : '(' ;
RPAREN  : ')' ;
SEMI    : ';' ;
COMMA   : ',' ;
LCBRACK : '{' ;
RCBRACK : '}' ;
LSBRACK : '[' ;
RSBRACK : ']' ;

// Identificadores e números
ID  : [a-zA-Z_][a-zA-Z0-9_]* ;
NUM : [0-9]+ ;

// Comentários e espaços
LINE_COMM  : '//' ~[\r\n]* -> skip ;
BLOCK_COMM : '/*' .*? '*/' -> skip ;
WS         : [ \t\r\n\f]+ -> skip ;


/*
 * ==========================================================
 * Regras sintáticas
 * ==========================================================
 * O parser usa os tokens para reconhecer a estrutura do programa.
 */

program
    : list_decls+=decl+
    ;

decl
    : var_decl
    | funct_decl
    ;

var_decl
    : type_especifier ID SEMI
    | type_especifier ID LSBRACK NUM RSBRACK SEMI
    ;

type_especifier
    : INT
    | VOID
    ;

funct_decl
    : type_especifier ID LPAREN params RPAREN comp_decl
    ;

params
    : params_list+=param (COMMA params_list+=param)*
    | VOID
    ;

param
    : type_especifier ID
    | type_especifier ID LSBRACK RSBRACK
    ;

comp_decl
    : LCBRACK loc_decls+=local_decl* stmts_list+=stmt_list* RCBRACK
    ;

local_decl
    : decl_list+=var_decl+
    ;

stmt_list
    : stmts_list+=stmt+
    ;

stmt
    : exp_decl
    | comp_decl
    | select_decl
    | iter_decl
    | ret_decl
    ;

exp_decl
    : exp SEMI
    | SEMI
    ;

select_decl
    : IF LPAREN condition=exp RPAREN LCBRACK if_body+=stmt* RCBRACK
      (ELSE LCBRACK else_body+=stmt* RCBRACK)?
    ;

iter_decl
    : WHILE LPAREN exp RPAREN stmt
    ;

ret_decl
    : RETURN SEMI
    | RETURN exp SEMI
    ;

exp
    : var ASSIGN exp
    | simple_exp
    ;

var
    : ID
    | ID LSBRACK exp RSBRACK
    ;

simple_exp
    : sum_exp_left=sum_exp relational sum_exp_right=sum_exp
    | g_exp=sum_exp
    ;

relational
    : LET
    | LT
    | GT
    | GET
    | EQ
    | NEQ
    ;

sum_exp
    : sum_exp op=(PLUS | MINUS) term
    | term
    ;

term
    : term op=(OVER | TIMES) fact
    | fact
    ;

fact
    : LPAREN exp RPAREN
    | var
    | activation
    | NUM
    ;

activation
    : ID LPAREN args+=exp (COMMA args+=exp)* RPAREN
    | ID LPAREN RPAREN
    ;
