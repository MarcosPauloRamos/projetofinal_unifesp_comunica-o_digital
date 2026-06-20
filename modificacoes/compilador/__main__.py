import sys
import argparse
import antlr4

from .cminus_semantic import SymbolTableGenerator
from .cminus_abstract_st import AbstractStNodeConstructVisitor
from .abstract_printer import AbstractStPrinter
from .cminus_intermediate import IntermediateCodeGenerator
from .cminus_assembler import AssemblyGenerator
from .gen.cminusParser import cminusParser
from .gen.cminusLexer import cminusLexer


def criar_parser_argumentos():
    parser = argparse.ArgumentParser(description='Compilador Cminus para BM_CORE')

    parser.add_argument('--file')

    parser.add_argument('--lex', action='store_true')
    parser.add_argument('--syn', action='store_true')
    parser.add_argument('--sem', action='store_true')
    parser.add_argument('--inter', action='store_true')
    parser.add_argument('--synth', action='store_true')

    parser.add_argument('--mem', action='store', default=0, required=False)
    parser.add_argument('--stack', action='store', default=0, required=False)

    # mode = 'os'   -> operações de entrada/saída reais
    # mode = 'prog' -> operações de entrada/saída por syscall
    parser.add_argument('--mode', action='store', default='os', required=False)

    return parser


def gerar_arvore_parse(caminho_arquivo):
    entrada = antlr4.FileStream(caminho_arquivo)
    analisador_lexico = cminusLexer(entrada)
    fluxo_tokens = antlr4.CommonTokenStream(analisador_lexico)
    analisador_sintatico = cminusParser(fluxo_tokens)

    arvore_parse = analisador_sintatico.program()

    return fluxo_tokens, arvore_parse


def imprimir_tokens(fluxo_tokens):
    fluxo_tokens.fill()

    for token in fluxo_tokens.tokens:
        print(token.line, ":", token.text)


def imprimir_codigo_fonte(caminho_arquivo):
    with open(caminho_arquivo, 'r') as arquivo:
        print(' ')
        print(arquivo.read())


def main(argv):
    parser = criar_parser_argumentos()
    argumentos = parser.parse_args()

    fluxo_tokens, arvore_parse = gerar_arvore_parse(argumentos.file)

    if argumentos.lex:
        imprimir_tokens(fluxo_tokens)

    arvore_abstrata = AbstractStNodeConstructVisitor().visit(arvore_parse)

    if argumentos.syn:
        AbstractStPrinter().visit(arvore_abstrata)

    analise_semantica = SymbolTableGenerator(arvore_abstrata, argumentos.mem)

    if argumentos.sem:
        print(analise_semantica)

    if analise_semantica.errors:
        print('Ainda existem erros semânticos...')
        for erro in analise_semantica.errors:
            print(erro)
        return

    if argumentos.inter:
        imprimir_codigo_fonte(argumentos.file)

        codigo_intermediario = IntermediateCodeGenerator(arvore_abstrata)
        print_imediate(codigo_intermediario)

    if argumentos.synth:
        if not argumentos.inter:
            imprimir_codigo_fonte(argumentos.file)

        codigo_intermediario = IntermediateCodeGenerator(arvore_abstrata)

        assembly = AssemblyGenerator(
            analise_semantica,
            codigo_intermediario.intermediate_list,
            argumentos.stack,
            argumentos.mode
        )

        print_asm(assembly)


def print_asm(asm):
    instrucoes_sem_operando = [
        'nop',
        'hlt',
        'btm',
        'cwsfh',
        'crsfh',
        'gint',
        'endp',
        'getpc',
        'setpc'
    ]

    with open('bmcore_asm.txt', 'w') as arquivo_saida:
        for instrucao in asm.asm_list:
            if len(instrucao) == 1 and instrucao[0] not in instrucoes_sem_operando:
                arquivo_saida.write(instrucao[0])
                arquivo_saida.write('\n')
            else:
                arquivo_saida.write('    ')
                for campo in instrucao:
                    arquivo_saida.write(str(campo) + ' ')
                arquivo_saida.write('\n')


def print_imediate(inter):
    for indice, instrucao in enumerate(inter.intermediate_list):
        print(indice, ' : (', end='')
        print(*instrucao, sep=', ', end='')
        print(') ')


if __name__ == '__main__':
    main(sys.argv)
