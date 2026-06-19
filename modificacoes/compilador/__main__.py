import sys
import argparse
import antlr4

# Módulos do compilador
from .cminus_semantic import SymbolTableGenerator
from .cminus_abstract_st import AbstractStNodeConstructVisitor
from .abstract_printer import AbstractStPrinter
from .cminus_intermediate import IntermediateCodeGenerator
from .cminus_assembler import AssemblyGenerator

# Arquivos gerados pelo ANTLR
from .gen.cminusParser import cminusParser
from .gen.cminusLexer import cminusLexer


def main(argv):
    """
    Função principal do compilador.
    """

    # ==========================================================
    # Configuração dos parâmetros da linha de comando
    # ==========================================================

    parser = argparse.ArgumentParser(description="Compilador Cminus")

    parser.add_argument("--file", help="Arquivo Cminus a ser compilado")

    parser.add_argument("--lex", action="store_true",
                        help="Executa apenas a análise léxica")

    parser.add_argument("--syn", action="store_true",
                        help="Mostra a árvore sintática abstrata (AST)")

    parser.add_argument("--sem", action="store_true",
                        help="Executa a análise semântica")

    parser.add_argument("--inter", action="store_true",
                        help="Gera o código intermediário")

    parser.add_argument("--synth", action="store_true",
                        help="Gera o código Assembly")

    parser.add_argument("--mem",
                        action="store",
                        default=0,
                        help="Endereço inicial da memória de dados")

    parser.add_argument("--stack",
                        action="store",
                        default=0,
                        help="Valor inicial da pilha")

    parser.add_argument("--mode",
                        action="store",
                        default="os",
                        help="Modo de geração (os ou prog)")

    argumentos = parser.parse_args()

    # ==========================================================
    # Leitura do arquivo fonte
    # ==========================================================

    arquivo_fonte = antlr4.FileStream(argumentos.file)

    # ==========================================================
    # Análise Léxica
    # ==========================================================

    analisador_lexico = cminusLexer(arquivo_fonte)

    fluxo_tokens = antlr4.CommonTokenStream(analisador_lexico)

    # ==========================================================
    # Análise Sintática
    # ==========================================================

    analisador_sintatico = cminusParser(fluxo_tokens)

    arvore_parse = analisador_sintatico.program()

    # ----------------------------------------------------------

    if argumentos.lex:
        print("\n===== TOKENS =====\n")

        for token in fluxo_tokens.tokens:
            print(token.line, ":", token.text)

    # ==========================================================
    # Construção da AST
    # ==========================================================

    construtor_ast = AbstractStNodeConstructVisitor()

    arvore_abstrata = construtor_ast.visit(arvore_parse)

    # ==========================================================
    # Impressão da AST
    # ==========================================================

    if argumentos.syn:
        print("\n===== ÁRVORE SINTÁTICA ABSTRATA =====\n")
        AbstractStPrinter().visit(arvore_abstrata)

    # ==========================================================
    # Análise Semântica
    # ==========================================================

    endereco_inicial_memoria = argumentos.mem

    analise_semantica = SymbolTableGenerator(
        arvore_abstrata,
        endereco_inicial_memoria
    )

    if argumentos.sem:
        print(analise_semantica)

    # ==========================================================
    # Verificação de erros semânticos
    # ==========================================================

    if analise_semantica.errors:

        print("\nExistem erros semânticos encontrados:\n")

        for erro in analise_semantica.errors:
            print(erro)

        return

    # ==========================================================
    # Código Intermediário
    # ==========================================================

    if argumentos.inter:

        with open(argumentos.file, "r") as arquivo:
            print("\n===== CÓDIGO FONTE =====\n")
            print(arquivo.read())

        codigo_intermediario = IntermediateCodeGenerator(arvore_abstrata)

        imprimir_codigo_intermediario(codigo_intermediario)

    # ==========================================================
    # Geração do Assembly
    # ==========================================================

    if argumentos.synth:

        if not argumentos.inter:
            with open(argumentos.file, "r") as arquivo:
                print("\n===== CÓDIGO FONTE =====\n")
                print(arquivo.read())

        codigo_intermediario = IntermediateCodeGenerator(arvore_abstrata)

        assembly = AssemblyGenerator(
            analise_semantica,
            codigo_intermediario.intermediate_list,
            argumentos.stack,
            argumentos.mode
        )

        salvar_assembly(assembly)


def salvar_assembly(assembly):
    """
    Salva o Assembly gerado em um arquivo.
    """

    instrucoes_sem_operandos = [
        "nop",
        "hlt",
        "btm",
        "cwsfh",
        "crsfh",
        "gint",
        "endp",
        "getpc",
        "setpc"
    ]

    with open("bmcore_asm.txt", "w") as arquivo_saida:

        for instrucao in assembly.asm_list:

            if len(instrucao) == 1 and instrucao[0] not in instrucoes_sem_operandos:

                arquivo_saida.write(instrucao[0])
                arquivo_saida.write("\n")

            else:

                arquivo_saida.write("    ")

                for campo in instrucao:
                    arquivo_saida.write(str(campo) + " ")

                arquivo_saida.write("\n")


def imprimir_codigo_intermediario(codigo_intermediario):
    """
    Imprime o código intermediário.
    """

    for indice, instrucao in enumerate(codigo_intermediario.intermediate_list):

        print(
            indice,
            ": (",
            ", ".join(map(str, instrucao)),
            ")",
            sep=""
        )


if __name__ == "__main__":
    main(sys.argv)
