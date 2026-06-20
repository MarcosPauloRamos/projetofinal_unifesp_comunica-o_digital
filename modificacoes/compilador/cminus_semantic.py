from tabulate import tabulate

from . import cminus_abstract_st


class Symbol:
    def __init__(
        self,
        name,
        scope,
        line,
        id_type,
        data_type,
        mem_location=-1,
        params=None
    ):
        self.name = name
        self.scope = scope
        self.lines = {line}
        self.id_type = id_type
        self.data_type = data_type
        self.mem_location = mem_location
        self.params = [params]

    def as_tuple(self):
        return (
            self.name,
            self.scope,
            ', '.join(map(str, sorted(self.lines))),
            self.id_type,
            self.data_type,
            self.mem_location,
            ', '.join(map(str, self.params))
        )


class SymbolTableGenerator(cminus_abstract_st.AbstractStVisitor):
    """
    Percorre a AST, gera a tabela de símbolos e verifica erros semânticos.

    Também define as posições de memória das variáveis, com base no valor
    inicial recebido por --mem.
    """

    def __init__(self, abstract_st, mem_init):
        self.table = {}
        self.errors = []

        self._scope = ''
        self._mem_loc = int(mem_init)

        self.source_functions = [
            'input',
            'output',
            'load_os',
            'end_bios',
            'move_HD_mem',
            'store_HD',
            'move_reg_proc_OS',
            'move_reg_OS_proc',
            'swap_process',
            'write_lcd',
            'concatenate',
            'get_interruption',
            'load_reg_context',
            'store_reg_context',
            'recover_OS',
            'set_proc_pc',
            'get_proc_pc',
            'UART_input',
            'UART_output'
        ]

        self.registrar_funcoes_nativas()

        self.visit(abstract_st)

        if 'main' not in self.table:
            self.errors.append('No main function declared')

    def __str__(self):
        return tabulate(
            tabular_data=[
                (key,) + symbol.as_tuple()
                for key, symbol in self.table.items()
            ],
            headers=[
                'Key',
                'Id',
                'Scope',
                'Lines',
                'Id Type',
                'Var Type',
                'Mem Loc',
                'Parameters'
            ],
            tablefmt='grid',
        )

    # ==========================================================
    # Funções auxiliares
    # ==========================================================

    def registrar_funcoes_nativas(self):
        """
        Registra funções especiais reconhecidas pelo compilador.

        Essas funções não são declaradas no código Cminus, mas representam
        operações especiais da arquitetura BM_CORE/BM32OS.
        """
        for funcao in self.source_functions:
            self.table[funcao] = Symbol(
                funcao,
                'source',
                0,
                'funct',
                'Source function'
            )

    def scoped_name(self, name):
        """
        Retorna o nome completo de um símbolo considerando o escopo atual.
        """
        if not self._scope:
            return f'global.{name}'
        return f'{self._scope}.{name}'

    def obter_escopo_real(self):
        """
        Retorna o escopo atual. Caso esteja fora de funções, retorna global.
        """
        return self._scope if self._scope != '' else 'global'

    def buscar_nome_variavel(self, id_):
        """
        Busca uma variável primeiro no escopo local e depois no global.
        Retorna a chave usada na tabela de símbolos ou None.
        """
        nome_local = self.scoped_name(id_)
        nome_global = f'global.{id_}'

        if nome_local in self.table:
            return nome_local

        if nome_global in self.table:
            return nome_global

        return None

    def check_activation(self, node: cminus_abstract_st.Exp):
        """
        Verifica se uma expressão simples contém chamada direta de função.

        Mantido com a mesma lógica original para preservar o comportamento.
        """
        if node.simple_exp:
            if node.simple_exp.generic_exp:
                if node.simple_exp.generic_exp.term:
                    if node.simple_exp.generic_exp.term.fact:
                        if node.simple_exp.generic_exp.term.fact.activ:
                            return True
        return False

    # ==========================================================
    # Visitors da AST
    # ==========================================================

    def visit_Program(self, node: cminus_abstract_st.Program):
        for decl in node.decls:
            self.visit(decl)

    def visit_Decl(self, node: cminus_abstract_st.Decl):
        if node.var_decl:
            self.visit(node.var_decl)
        elif node.funct_decl:
            self.visit(node.funct_decl)

    def visit_Var_decl(self, node: cminus_abstract_st.Var_decl):
        nome = self.scoped_name(node.id_)

        if nome in self.table:
            self.errors.append(
                f'{node.line}: Variable "{node.id_}" already declared'
            )
            return False

        if node.id_ in self.table:
            self.errors.append(
                f'{node.line}: Variable "{node.id_}" shares name with a function'
            )

        if node.type_.type_ == 'void':
            self.errors.append(
                f'{node.line}: Void variable cannot be declared'
            )

        escopo_real = self.obter_escopo_real()

        if node.num:
            posicao_inicial = self._mem_loc
            self._mem_loc += int(node.num)

            self.table[nome] = Symbol(
                node.id_,
                escopo_real,
                node.line,
                'var[]',
                node.type_.type_,
                [posicao_inicial, self._mem_loc - 1]
            )
        else:
            self.table[nome] = Symbol(
                node.id_,
                escopo_real,
                node.line,
                'var',
                node.type_.type_,
                self._mem_loc
            )
            self._mem_loc += 1

        return True

    def visit_Funct_decl(self, node: cminus_abstract_st.Funct_decl):
        if node.id_ in self.table:
            if node.id_ in self.source_functions:
                self.errors.append(
                    f'{node.line}: Function "{node.id_}" atempting to be an override to an source function'
                )
            else:
                self.errors.append(
                    f'{node.line}: Function "{node.id_}" already declared'
                )
            return

        escopo_funcao = 'global' if self._scope == '' else self._scope

        self.table[node.id_] = Symbol(
            node.id_,
            escopo_funcao,
            node.line,
            'funct',
            node.type_.type_
        )

        self._scope = node.id_

        self.visit(node.params)
        self.visit(node.comp_decls)

        self._scope = ''

    def visit_Params(self, node: cminus_abstract_st.Params):
        if node.par_list:
            for param in node.par_list:
                self.visit(param)

    def visit_Param(self, node: cminus_abstract_st.Param):
        if None in self.table[self._scope].params:
            self.table[self._scope].params.remove(None)

        self.table[self._scope].params.append(node.id_)

        nome = self.scoped_name(node.id_)

        if nome in self.table:
            self.errors.append(
                f'{node.line}: Variable "{node.id_}" already declared'
            )
            return False

        if node.type_.type_ == 'void':
            self.errors.append(
                f'{node.line}: Void variable cannot be used as a function parameter'
            )

        tipo_identificador = 'var[]' if node.isArray else 'var'

        self.table[nome] = Symbol(
            node.id_,
            self._scope,
            node.line,
            tipo_identificador,
            node.type_.type_,
            self._mem_loc
        )

        self._mem_loc += 1

    def visit_Comp_decl(self, node: cminus_abstract_st.Comp_decl):
        if node.local_decl:
            for decl in node.local_decl:
                self.visit(decl)

        if node.stmt_list:
            for stmt in node.stmt_list:
                self.visit(stmt)

    def visit_Local_decl(self, node: cminus_abstract_st.Local_decl):
        for decl in node.var_decls:
            self.visit(decl)

    def visit_Stmt_list(self, node: cminus_abstract_st.Stmt_list):
        for stmt in node.stmts:
            self.visit(stmt)

    def visit_Stmt(self, node: cminus_abstract_st.Stmt):
        self.visit(node.stmt_type)

    def visit_Exp_decl(self, node: cminus_abstract_st.Exp_decl):
        if node.exp:
            self.visit(node.exp)

    def visit_Select_decl(self, node: cminus_abstract_st.Select_decl):
        self.visit(node.condition)

        for stmt in node.if_body:
            self.visit(stmt)

        if node.else_body:
            for stmt in node.else_body:
                self.visit(stmt)

    def visit_Iter_decl(self, node: cminus_abstract_st.Iter_decl):
        self.visit(node.condition)
        self.visit(node.stmts)

    def visit_Ret_decl(self, node: cminus_abstract_st.Ret_decl):
        if node.exp:
            self.visit(node.exp)

    def visit_Exp(self, node: cminus_abstract_st.Exp):
        tipo_variavel = None

        if node.var:
            self.visit(node.var)

            nome_variavel = self.buscar_nome_variavel(node.var.id_)

            if nome_variavel:
                tipo_variavel = self.table[nome_variavel].data_type

        if node.simple_exp:
            self.visit(node.simple_exp)

        if node.exp:
            self.visit(node.exp)

        # Permite chamada de função void quando ela não é atribuída a variável.
        if self.check_activation(node):
            ativacao = node.simple_exp.generic_exp.term.fact.activ

            if ativacao.id_ in self.table:
                chamada_funcao = self.table[ativacao.id_]
                tipo_retorno = chamada_funcao.data_type

                if tipo_retorno == 'void' and tipo_variavel == 'int':
                    self.errors.append(
                        f'{node.line}: Invalid assignment of type {tipo_retorno}'
                    )

    def visit_Var(self, node: cminus_abstract_st.Var):
        nome_variavel = self.buscar_nome_variavel(node.id_)

        if nome_variavel:
            self.table[nome_variavel].lines.add(node.line)
            return True

        self.errors.append(
            f'{node.line}: Variable "{node.id_}" used whitout previous declaration'
        )
        return False

    def visit_Simple_exp(self, node: cminus_abstract_st.Simple_exp):
        if node.exp_left:
            self.visit(node.exp_left)
            self.visit(node.exp_right)
        else:
            self.visit(node.generic_exp)

    def visit_Sum_exp(self, node: cminus_abstract_st.Sum_exp):
        if node.op:
            self.visit(node.sum_exp)
            self.visit(node.term)
        else:
            self.visit(node.term)

    def visit_Term(self, node: cminus_abstract_st.Term):
        if node.op:
            self.visit(node.term)
            self.visit(node.fact)
        else:
            self.visit(node.fact)

    def visit_Fact(self, node: cminus_abstract_st.Fact):
        if node.exp:
            self.visit(node.exp)

        if node.var:
            self.visit(node.var)

        if node.activ:
            self.visit(node.activ)

    def visit_Activation(self, node: cminus_abstract_st.Activation):
        nome_funcao = node.id_

        if nome_funcao not in self.table:
            self.errors.append(
                f'{node.line}: Function "{node.id_}" used whitout declaration'
            )
            return False

        self.table[nome_funcao].lines.add(node.line)

        # Funções nativas são tratadas diretamente no gerador de assembly.
        if nome_funcao == 'input' or nome_funcao in self.source_functions:
            return

        parametros = self.table[nome_funcao].params

        if len(parametros) == 1 and parametros[0] is None:
            qtd_parametros_esperada = 0
        else:
            qtd_parametros_esperada = len(parametros)

        qtd_parametros_recebida = 0

        for argumento in node.args_list:
            qtd_parametros_recebida += 1
            self.visit(argumento)

        if qtd_parametros_recebida != qtd_parametros_esperada:
            self.errors.append(
                f'{node.line}: Function "{node.id_}" expects {qtd_parametros_esperada} arguments, but {qtd_parametros_recebida} were given'
            )
