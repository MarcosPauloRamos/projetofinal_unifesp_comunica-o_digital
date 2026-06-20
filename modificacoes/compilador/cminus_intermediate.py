from . import cminus_abstract_st


class IntermediateCodeGenerator(cminus_abstract_st.AbstractStVisitor):
    """
    Gera o código intermediário a partir da AST.

    O código intermediário usa instruções de 4 campos no formato:

        [operação, operando_1, operando_2, resultado]

    Exemplo:

        ['addition', 'a', 'b', 't0']

    representa:

        t0 = a + b
    """

    def __init__(self, abstract_st):
        super().__init__()

        self.intermediate_list = []
        self.temp_num = 0
        self.label_num = 1

        self.visit(abstract_st)

    # ==========================================================
    # Funções auxiliares de geração
    # ==========================================================

    def adicionar_instrucao(self, operacao, campo_1='_', campo_2='_', campo_3='_'):
        instrucao = [operacao, campo_1, campo_2, campo_3]
        self.intermediate_list.append(instrucao)
        return instrucao

    def novo_temporario(self):
        temporario = f't{self.temp_num}'
        self.temp_num += 1
        return temporario

    def temporario_atual(self):
        return f't{self.temp_num}'

    def nova_label(self):
        label = f'L{self.label_num}'
        self.label_num += 1
        return label

    def obter_valor_de_fator(self, fator):
        """
        Retorna o valor representado por um nó Fact.
        Pode ser número, variável, ativação de função ou expressão.
        """
        if fator is None:
            return None

        if fator.num:
            return fator.num

        if fator.var:
            return fator.var.id_

        if fator.activ:
            return fator.activ.id_

        if fator.exp:
            fator_interno = self.get_non_exp_factor(fator.exp)
            return self.obter_valor_de_fator(fator_interno)

        return None

    def substituir_fator_por_temporario(self, fator, temporario):
        """
        Substitui o conteúdo de um fator pelo temporário gerado.
        Mantém o comportamento original, que atualizava a própria AST.
        """
        if fator is None:
            return

        if fator.var:
            fator.var.id_ = temporario
        elif fator.num:
            fator.num = temporario
        elif fator.activ:
            fator.activ.id_ = temporario
        elif fator.exp:
            fator_interno = self.get_non_exp_factor(fator.exp)
            self.substituir_fator_por_temporario(fator_interno, temporario)

    def obter_lado_relacional(self, expressao):
        fator = self.get_factor_child(expressao)
        return self.obter_valor_de_fator(fator)

    def gerar_operacao_binaria(self, node, no_esquerdo, no_direito, operador):
        """
        Gera operações aritméticas binárias.

        Usado por visit_Sum_exp e visit_Term.
        """
        self.visit(no_direito)
        self.visit(no_esquerdo)

        fator_direito = self.get_factor_child(node)
        fator_esquerdo = self.get_factor_child(no_esquerdo)

        direito = self.obter_valor_de_fator(fator_direito)
        esquerdo = self.obter_valor_de_fator(fator_esquerdo)

        temporario = self.temporario_atual()

        self.substituir_fator_por_temporario(fator_direito, temporario)
        self.substituir_fator_por_temporario(fator_esquerdo, temporario)

        self.adicionar_instrucao(operador, esquerdo, direito, temporario)
        self.temp_num += 1

    # ==========================================================
    # Visitors básicos
    # ==========================================================

    def visit_Program(self, node: cminus_abstract_st.Program):
        for decl in node.decls:
            self.visit(decl)

    def visit_Decl(self, node: cminus_abstract_st.Decl):
        if node.funct_decl is None:
            self.visit(node.var_decl)
        else:
            self.visit(node.funct_decl)

    def visit_Var_decl(self, node: cminus_abstract_st.Var_decl):
        self.visit(node.type_)

    def visit_Type_especifier(self, node: cminus_abstract_st.Var_decl):
        return node.type_

    def visit_Funct_decl(self, node: cminus_abstract_st.Funct_decl):
        self.adicionar_instrucao('function', node.id_, '_', '_')
        self.visit(node.params)
        self.visit(node.comp_decls)

    def visit_Params(self, node: cminus_abstract_st.Params):
        if node.par_list is not None:
            for param in node.par_list:
                self.visit(param)

    def visit_Param(self, node: cminus_abstract_st.Params):
        self.visit(node.type_)

    def visit_Comp_decl(self, node: cminus_abstract_st.Comp_decl):
        for decl in node.local_decl:
            self.visit(decl)

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

    # ==========================================================
    # Controle de fluxo
    # ==========================================================

    def visit_Select_decl(self, node: cminus_abstract_st.Select_decl):
        self.visit(node.condition)

        if node.condition.simple_exp and node.condition.simple_exp.relational:
            expressao = node.condition.simple_exp

            esquerdo = self.obter_lado_relacional(expressao.exp_left)
            direito = self.obter_lado_relacional(expressao.exp_right)
            operador = self.get_relational_operator(expressao.relational)

            temporario = self.temporario_atual()
            label_falso = f'L{self.label_num + 1}'

            self.adicionar_instrucao(operador, esquerdo, direito, temporario)
            self.adicionar_instrucao('jump_if_false', temporario, label_falso, '_')

            self.temp_num += 1
            self.label_num += 1

        for stmt in node.if_body:
            self.visit(stmt)

        self.label_num += 1

        if node.else_body:
            label_saida = f'L{self.label_num}'

            self.adicionar_instrucao('goto', label_saida, '_', '_')
            self.adicionar_instrucao('label', label_falso, '_', '_')
            self.adicionar_instrucao('end_label', label_falso, '_', '_')

            for stmt in node.else_body:
                self.visit(stmt)

            self.adicionar_instrucao('label', label_saida, '_', '_')
            self.adicionar_instrucao('end_label', label_saida, '_', '_')
        else:
            self.adicionar_instrucao('label', label_falso, '_', '_')
            self.adicionar_instrucao('end_label', label_falso, '_', '_')

    def visit_Iter_decl(self, node: cminus_abstract_st.Iter_decl):
        self.label_num += 1

        label_inicio = f'L{self.label_num}'
        self.adicionar_instrucao('label', label_inicio, '_', '_')

        self.visit(node.condition)

        if node.condition.simple_exp and node.condition.simple_exp.relational:
            expressao = node.condition.simple_exp

            esquerdo = self.obter_lado_relacional(expressao.exp_left)
            direito = self.obter_lado_relacional(expressao.exp_right)
            operador = self.get_relational_operator(expressao.relational)

            label_fim = f'L{self.label_num + 1}'
            temporario = self.temporario_atual()

            self.adicionar_instrucao(operador, esquerdo, direito, temporario)
            self.adicionar_instrucao('jump_if_false', temporario, label_fim, '_')

            self.temp_num += 1
            self.label_num += 2

            self.visit(node.stmts)

            self.adicionar_instrucao('goto', label_inicio, '_', '_')
            self.adicionar_instrucao('end_label', label_inicio, '_', '_')
            self.adicionar_instrucao('label', label_fim, '_', '_')
            self.adicionar_instrucao('end_label', label_fim, '_', '_')

    def visit_Ret_decl(self, node: cminus_abstract_st.Ret_decl):
        valor = None

        if node.exp:
            self.visit(node.exp)

            fator = self.get_factor_child(node.exp)
            valor = self.obter_valor_de_fator(fator)

        self.adicionar_instrucao('return', valor if valor else '_', '_', '_')

    # ==========================================================
    # Expressões e variáveis
    # ==========================================================

    def visit_Exp(self, node: cminus_abstract_st.Exp):
        if node.simple_exp:
            self.visit(node.simple_exp)
            return

        self.visit(node.exp)
        self.visit(node.var)

        fator = self.get_multiple_assign_factor(node.exp)
        valor = self.obter_valor_de_fator(fator)

        tipo_atribuicao = 'array_assign' if node.var.exp else 'assign'

        self.adicionar_instrucao(
            tipo_atribuicao,
            node.var.id_,
            valor if valor else '_',
            '_'
        )

        if tipo_atribuicao == 'array_assign':
            self.temp_num += 1

    def visit_Var(self, node: cminus_abstract_st.Var):
        if node.exp:
            self.visit(node.exp)

            fator = self.get_factor_child(node.exp)
            indice = self.obter_valor_de_fator(fator)

            temporario = self.temporario_atual()

            self.adicionar_instrucao(
                'weak_assign',
                temporario,
                node.id_,
                indice
            )

            node.id_ = temporario
            self.temp_num += 1

    def visit_Simple_exp(self, node: cminus_abstract_st.Simple_exp):
        if node.relational:
            self.visit(node.exp_left)
            self.visit(node.exp_right)
        else:
            self.visit(node.generic_exp)

    def visit_Sum_exp(self, node: cminus_abstract_st.Sum_exp):
        if node.op:
            operador = 'addition' if node.op == '+' else 'subtraction'
            self.gerar_operacao_binaria(
                node=node,
                no_esquerdo=node.sum_exp,
                no_direito=node.term,
                operador=operador
            )
        else:
            self.visit(node.term)

    def visit_Term(self, node: cminus_abstract_st.Term):
        if node.op:
            operador = 'multiplication' if node.op == '*' else 'division'
            self.gerar_operacao_binaria(
                node=node,
                no_esquerdo=node.term,
                no_direito=node.fact,
                operador=operador
            )
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
        for arg in node.args_list:
            self.visit(arg)

            fator = self.get_factor_child(arg)
            valor = self.obter_valor_de_fator(fator)

            self.adicionar_instrucao('arg', node.id_, valor, '_')

        temporario = self.temporario_atual()

        self.adicionar_instrucao(
            'call',
            node.id_,
            len(node.args_list),
            temporario
        )

        node.id_ = temporario
        self.temp_num += 1

    # ==========================================================
    # Funções auxiliares de navegação na AST
    # ==========================================================

    def get_factor_child(self, node):
        """
        Retorna um nó Fact a partir de uma expressão.
        """
        if type(node).__name__ == 'Exp':
            if node.exp:
                return self.get_factor_child(node.exp)
            return self.get_factor_child(node.simple_exp)

        if type(node).__name__ == 'Simple_exp':
            if node.exp_left:
                self.get_factor_child(node.exp_left)
                return self.get_factor_child(node.exp_right)
            return self.get_factor_child(node.generic_exp)

        if type(node).__name__ == 'Sum_exp':
            if node.sum_exp:
                self.get_factor_child(node.sum_exp)
            if node.term:
                return self.get_factor_child(node.term)

        if type(node).__name__ == 'Term':
            if node.term:
                self.get_factor_child(node.term)
            if node.fact:
                return node.fact

        if type(node).__name__ == 'Fact':
            return node

        return None

    def get_non_exp_factor(self, node):
        """
        Retorna um Fact cujo filho não seja outra expressão.
        """
        if type(node).__name__ == 'Exp':
            if node.exp:
                return self.get_non_exp_factor(node.exp)
            return self.get_non_exp_factor(node.simple_exp)

        if type(node).__name__ == 'Simple_exp':
            if node.exp_left:
                self.get_non_exp_factor(node.exp_left)
                return self.get_non_exp_factor(node.exp_right)
            return self.get_non_exp_factor(node.generic_exp)

        if type(node).__name__ == 'Sum_exp':
            if node.sum_exp:
                self.get_non_exp_factor(node.sum_exp)
            if node.term:
                return self.get_non_exp_factor(node.term)

        if type(node).__name__ == 'Term':
            if node.term:
                self.get_non_exp_factor(node.term)
            if node.fact:
                return self.get_non_exp_factor(node.fact)

        if type(node).__name__ == 'Fact':
            if node.exp is None:
                return node
            return self.get_non_exp_factor(node.exp)

        return None

    def get_multiple_assign_factor(self, node):
        """
        Retorna o último fator de uma atribuição múltipla.
        Exemplo: a = b = c = 1;
        """
        if type(node).__name__ == 'Exp':
            if node.exp:
                return self.get_multiple_assign_factor(node.exp)
            return self.get_factor_child(node.simple_exp)

        return None

    def get_relational_operator(self, node: cminus_abstract_st.Relational):
        operadores = {
            '<=': 'less_or_equal_than',
            '<': 'less_than',
            '>': 'greater_than',
            '>=': 'greater_or_equal_than',
            '==': 'equal',
            '!=': 'not_equal',
        }

        return operadores[node.type_]
