from . import cminus_abstract_st


IDENT = 2


class AbstractStPrinter(cminus_abstract_st.AbstractStVisitor):
    """
    Percorre a AST e imprime sua estrutura de forma legível.
    Este arquivo é usado principalmente para depuração da análise sintática.
    """

    def __init__(self):
        super().__init__()
        self.ident = 0

    def imprimir(self, texto, *valores):
        print(' |' * self.ident, texto, *valores)

    def aumentar_identacao(self):
        self.ident += IDENT

    def diminuir_identacao(self):
        self.ident -= IDENT

    def visit_Program(self, node: cminus_abstract_st.Program):
        print('Program:')
        self.aumentar_identacao()

        self.imprimir('Declarations:')
        for decl in node.decls:
            self.visit(decl)

        self.diminuir_identacao()

    def visit_Decl(self, node: cminus_abstract_st.Decl):
        if node.funct_decl is None:
            self.visit(node.var_decl)
        else:
            self.visit(node.funct_decl)

    def visit_Var_decl(self, node: cminus_abstract_st.Var_decl):
        self.aumentar_identacao()

        if node.num is None:
            self.imprimir('Variable declaration:{')
            self.imprimir('Id:{', node.id_ + ' }')
            self.imprimir('Type:', self.visit(node.type_))
            self.imprimir('}')
        else:
            self.imprimir('Array variable declaration:{')
            self.imprimir('Id:{', node.id_ + ' }')
            self.imprimir('Type:', self.visit(node.type_))
            self.imprimir('Array size:', node.num)
            self.imprimir('}')

        self.diminuir_identacao()

    def visit_Type_especifier(self, node: cminus_abstract_st.Type_especifier):
        return node.type_

    def visit_Funct_decl(self, node: cminus_abstract_st.Funct_decl):
        self.aumentar_identacao()

        self.imprimir('Function declaration:{')
        self.imprimir('Id:{', node.id_ + ' }')
        self.imprimir('Type:{', self.visit(node.type_) + ' }')

        self.imprimir('Function parameters:{')
        self.visit(node.params)
        self.imprimir('}')

        self.imprimir('Function body:{')
        self.visit(node.comp_decls)
        self.imprimir('}')

        self.diminuir_identacao()

    def visit_Params(self, node: cminus_abstract_st.Params):
        if node.par_list is not None:
            for param in node.par_list:
                self.visit(param)

    def visit_Param(self, node: cminus_abstract_st.Param):
        self.aumentar_identacao()

        self.imprimir('Parameter:{')
        self.imprimir('Id:{', node.id_ + ' }')

        if not node.isArray:
            self.imprimir('Type:{', self.visit(node.type_) + ' }')
        else:
            self.imprimir('Type:{', self.visit(node.type_) + '[]' + ' }')

        self.imprimir('}')
        self.diminuir_identacao()

    def visit_Comp_decl(self, node: cminus_abstract_st.Comp_decl):
        self.aumentar_identacao()

        self.imprimir('Declarations:{')

        for decl in node.local_decl:
            self.visit(decl)

        for stmt in node.stmt_list:
            self.visit(stmt)

        self.imprimir('}')
        self.diminuir_identacao()

    def visit_Local_decl(self, node: cminus_abstract_st.Local_decl):
        self.aumentar_identacao()

        self.imprimir('Local declarations:{')
        for decl in node.var_decls:
            self.visit(decl)
        self.imprimir('}')

        self.diminuir_identacao()

    def visit_Stmt_list(self, node: cminus_abstract_st.Stmt_list):
        self.aumentar_identacao()

        self.imprimir('Statements:{')
        for stmt in node.stmts:
            self.visit(stmt)
        self.imprimir('}')

        self.diminuir_identacao()

    def visit_Stmt(self, node: cminus_abstract_st.Stmt):
        self.aumentar_identacao()

        self.imprimir('Statement type:{')
        self.visit(node.stmt_type)
        self.imprimir('}')

        self.diminuir_identacao()

    def visit_Exp_decl(self, node: cminus_abstract_st.Exp_decl):
        self.aumentar_identacao()

        self.imprimir('Expression:{')
        if node.exp:
            self.visit(node.exp)
        self.imprimir('}')

        self.diminuir_identacao()

    def visit_Select_decl(self, node: cminus_abstract_st.Select_decl):
        self.aumentar_identacao()

        self.imprimir('If:{')

        self.imprimir('Condition:{')
        self.visit(node.condition)
        self.imprimir('}')

        self.imprimir('If body:{')
        for stmt in node.if_body:
            self.visit(stmt)
        self.imprimir('}')

        self.imprimir('Else body:{')
        for stmt in node.else_body:
            self.visit(stmt)
        self.imprimir('}')

        self.imprimir('}')
        self.diminuir_identacao()

    def visit_Iter_decl(self, node: cminus_abstract_st.Iter_decl):
        self.aumentar_identacao()

        self.imprimir('While:{')

        self.imprimir('Condition:{')
        self.visit(node.condition)
        self.imprimir('}')

        self.imprimir('Iteration body:{')
        self.visit(node.stmts)
        self.imprimir('}')

        self.imprimir('}')
        self.diminuir_identacao()

    def visit_Ret_decl(self, node: cminus_abstract_st.Ret_decl):
        self.aumentar_identacao()

        self.imprimir('Return:{')

        if node.exp:
            self.imprimir('Expression:{')
            self.visit(node.exp)
            self.imprimir('}')
        else:
            self.imprimir('Empty')

        self.imprimir('}')
        self.diminuir_identacao()

    def visit_Exp(self, node: cminus_abstract_st.Exp):
        self.aumentar_identacao()

        self.imprimir('Assignment:{')

        if node.var:
            self.visit(node.var)

        if node.simple_exp:
            self.visit(node.simple_exp)
        elif node.exp:
            self.visit(node.exp)

        self.imprimir('}')
        self.diminuir_identacao()

    def visit_Var(self, node: cminus_abstract_st.Var):
        self.aumentar_identacao()

        if node.exp:
            self.imprimir('Array variable:{')
            self.imprimir('Id:{', node.id_ + ' }')
            self.imprimir('Array expression:')
            self.visit(node.exp)
            self.imprimir('}')
        else:
            self.imprimir('Variable:{')
            self.imprimir('Id:{', node.id_ + ' }')
            self.imprimir('}')

        self.diminuir_identacao()

    def visit_Simple_exp(self, node: cminus_abstract_st.Simple_exp):
        if node.exp_left:
            self.aumentar_identacao()

            self.imprimir('Left expression:{')
            self.visit(node.exp_left)
            self.imprimir('}')

            self.imprimir(
                'Relational operator:{',
                self.visit(node.relational) + ' }'
            )

            self.imprimir('Right expression:{')
            self.visit(node.exp_right)
            self.imprimir('}')

            self.diminuir_identacao()
        else:
            self.visit(node.generic_exp)

    def visit_Relational(self, node: cminus_abstract_st.Relational):
        return node.type_

    def visit_Sum_exp(self, node: cminus_abstract_st.Sum_exp):
        self.aumentar_identacao()

        if node.op:
            self.imprimir('Left expression:{')
            self.visit(node.sum_exp)
            self.imprimir('}')

            self.imprimir('Operator:{', node.op + ' }')

            self.imprimir('Right expression:{')
            self.visit(node.term)
            self.imprimir('}')
        else:
            self.visit(node.term)

        self.diminuir_identacao()

    def visit_Term(self, node: cminus_abstract_st.Term):
        self.aumentar_identacao()

        if node.op:
            self.imprimir('Left expression:{')
            self.visit(node.term)
            self.imprimir('}')

            self.imprimir('Operator:{', node.op + ' }')

            self.imprimir('Right expression:{')
            self.visit(node.fact)
            self.imprimir('}')
        else:
            self.visit(node.fact)

        self.diminuir_identacao()

    def visit_Fact(self, node: cminus_abstract_st.Fact):
        if node.exp:
            self.visit(node.exp)

        if node.var:
            self.visit(node.var)

        if node.activ:
            self.visit(node.activ)

        if node.num:
            self.aumentar_identacao()
            self.imprimir('Number:{', node.num + ' }')
            self.diminuir_identacao()

    def visit_Activation(self, node: cminus_abstract_st.Activation):
        self.aumentar_identacao()

        self.imprimir('Function call:{')
        self.imprimir('Id:{', node.id_ + ' }')

        self.imprimir('Arguments:{')
        for arg in node.args_list:
            self.visit(arg)
        self.imprimir('}')

        self.imprimir('}')
        self.diminuir_identacao()
