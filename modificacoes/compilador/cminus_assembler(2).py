import re


class AssemblyGenerator:
	"""
	Gera o assembly BM_CORE a partir do código intermediário.

	Esta versão V2 reorganiza o backend do compilador, mas deve manter
	a mesma lógica de geração do assembly original.
	"""

	def __init__(self, semantic_analysis, intermediate, init_stack, mode):
		self.source_functions = semantic_analysis.source_functions
		self.symbol_table = semantic_analysis.table
		self.intermediate_code = intermediate
		self.init_stack = init_stack
		self.mode = mode

		# Registradores temporários: 0 = livre, 1 = ocupado.
		self.temp_regs = [0] * 32

		# Estruturas auxiliares usadas durante a geração.
		self.source_funct_args = []
		self.reg_map = {}
		self.label_map = {}
		self.ra_stored = {}
		self.array_temp = []
		self.actual_scope = ''

		self.comparisons = [
			'less_or_equal_than',
			'less_than',
			'greater_than',
			'greater_or_equal_than',
			'equal',
			'not_equal'
		]

		self.asm_list = []

		self.inicializar_programa()
		self.synthesis()
		self.finalizar_programa()

	def inicializar_programa(self):
		self.asm_list.append(['ldi', '$sp,', f'{self.init_stack}'])
		self.asm_list.append(['jmp', 'main'])

	def finalizar_programa(self):
		self.asm_list.append(['nop'])
		self.asm_list.append(['endp'])
		self.asm_list.append(['nop'])
		self.asm_list.append(['hlt'])

	def emitir(self, *campos):
		self.asm_list.append(list(campos))

	def emitir_label(self, label):
		self.asm_list.append([f'{label}:'])

	def is_declared(self, token):
		if f'{self.actual_scope}.{token}' in self.symbol_table:
			return True

		if f'global.{token}' in self.symbol_table:
			return True

		return False

	def intermediate_tkn_type(self, token):
		if self.is_declared(token):
			return 'var'

		if re.match('t[0-9]', str(token)):
			return 'temp'

		return 'num'

	def build_table_key(self, token):
		local_key = f'{self.actual_scope}.{token}'
		global_key = f'global.{token}'

		if local_key in self.symbol_table:
			return local_key

		if global_key in self.symbol_table:
			return global_key

		return None

	def set_reg_free(self, reg_number):
		self.temp_regs[int(reg_number)] = 0

	def set_reg_busy(self, reg_number):
		self.temp_regs[int(reg_number)] = 1

	def get_free_reg(self):
		for i in range(1, len(self.temp_regs)):
			if self.temp_regs[i] == 0:
				return i

		raise RuntimeError('Não há registradores livres disponíveis.')

	def get_symbol_id_type(self, symbol):
		return symbol.id_type

	def get_symbol_data_type(self, symbol):
		return symbol.data_type

	def get_symbol_mem_location(self, symbol):
		return symbol.mem_location

	def get_symbol_parameters(self, symbol):
		return symbol.params

	def obter_simbolo(self, token):
		key = self.build_table_key(token)
		return self.symbol_table[key] if key else None

	def obter_posicao_memoria(self, token):
		return self.get_symbol_mem_location(self.obter_simbolo(token))

	def obter_inicio_vetor(self, token):
		mem_location = self.obter_posicao_memoria(token)

		if type(mem_location) is int:
			return mem_location

		return mem_location[0]
	# ==========================================================
	# Operandos
	# ==========================================================

	def carregar_variavel(self, token):
		reg = self.get_free_reg()
		self.set_reg_busy(reg)

		self.emitir(
			'ld',
			f'$r{reg},',
			'$r0,',
			self.obter_posicao_memoria(token)
		)

		return reg

	def carregar_imediato(self, valor):
		reg = self.get_free_reg()
		self.set_reg_busy(reg)

		self.emitir('ldi', f'$r{reg},', valor)

		return reg

	def carregar_temporario(self, token):
		reg = self.reg_map[token]

		if token in self.array_temp:
			aux_reg = self.get_free_reg()
			self.set_reg_busy(aux_reg)

			self.emitir('ld', f'$r{aux_reg},', f'$r{reg},', '0')

			self.set_reg_free(reg)
			self.reg_map[token] = -1

			return aux_reg

		return reg

	def carregar_operando(self, token):
		tipo = self.intermediate_tkn_type(token)

		if tipo == 'var':
			return self.carregar_variavel(token)

		if tipo == 'num':
			return self.carregar_imediato(token)

		if tipo == 'temp':
			return self.carregar_temporario(token)

		raise RuntimeError(f'Tipo de operando inválido: {token}')

	def liberar_operando(self, token, reg):
		if self.intermediate_tkn_type(token) == 'temp':
			self.reg_map[token] = -1

		self.set_reg_free(reg)

	def armazenar_variavel(self, token, reg):
		self.emitir(
			'str',
			'$r0,',
			str(self.obter_posicao_memoria(token)) + ',',
			f'$r{reg}'
		)

	# ==========================================================
	# Operações aritméticas
	# ==========================================================

	def gerar_operacao_aritmetica(self, inter, instrucao):
		operando_1 = inter[1]
		operando_2 = inter[2]
		destino = inter[3]

		reg_1 = self.carregar_operando(operando_1)
		reg_2 = self.carregar_operando(operando_2)

		self.emitir(
			instrucao,
			f'$r{reg_1},',
			f'$r{reg_1},',
			f'$r{reg_2}'
		)

		self.reg_map[destino] = reg_1

		if reg_2 != reg_1:
			self.set_reg_free(reg_2)

		if self.intermediate_tkn_type(operando_1) == 'temp':
			self.reg_map[operando_1] = -1

		if self.intermediate_tkn_type(operando_2) == 'temp':
			self.reg_map[operando_2] = -1

	def gerar_addition(self, inter):
		self.gerar_operacao_aritmetica(inter, 'add')

	def gerar_subtraction(self, inter):
		self.gerar_operacao_aritmetica(inter, 'sub')

	def gerar_multiplication(self, inter):
		self.gerar_operacao_aritmetica(inter, 'mult')

	def gerar_division(self, inter):
		self.gerar_operacao_aritmetica(inter, 'div')
	# ==========================================================
	# Atribuições e vetores
	# ==========================================================

	def gerar_assign(self, inter):
		destino = inter[1]
		origem = inter[2]

		reg_origem = self.carregar_operando(origem)
		self.armazenar_variavel(destino, reg_origem)

		self.liberar_operando(origem, reg_origem)

	def gerar_weak_assign(self, inter):
		temporario = inter[1]
		vetor = inter[2]
		indice = inter[3]

		reg_endereco = self.get_free_reg()
		self.set_reg_busy(reg_endereco)

		inicio_vetor = self.obter_inicio_vetor(vetor)

		if f'global.{vetor}' in self.symbol_table or self.actual_scope == 'main':
			self.emitir('ldi', f'$r{reg_endereco},', inicio_vetor)
		else:
			self.emitir('ld', f'$r{reg_endereco},', '$r0,', inicio_vetor)

		if self.intermediate_tkn_type(indice) == 'num':
			self.emitir(
				'addi',
				f'$r{reg_endereco},',
				f'$r{reg_endereco},',
				indice
			)
		else:
			reg_indice = self.carregar_operando(indice)

			self.emitir(
				'add',
				f'$r{reg_endereco},',
				f'$r{reg_endereco},',
				f'$r{reg_indice}'
			)

			self.liberar_operando(indice, reg_indice)

		self.reg_map[temporario] = reg_endereco
		self.array_temp.append(temporario)

	def gerar_array_assign(self, inter):
		temporario_endereco = inter[1]
		valor = inter[2]

		reg_endereco = self.reg_map[temporario_endereco]
		reg_valor = self.carregar_operando(valor)

		self.emitir(
			'str',
			f'$r{reg_endereco},',
			'0,',
			f'$r{reg_valor}'
		)

		self.set_reg_free(reg_endereco)
		self.liberar_operando(valor, reg_valor)

		self.reg_map[temporario_endereco] = -1

	# ==========================================================
	# Labels, saltos e comparações
	# ==========================================================

	def gerar_label(self, inter):
		self.emitir_label(inter[1])

	def gerar_end_label(self, inter):
		label_name = inter[1]

		if label_name in self.label_map:
			label_bool_reg = self.label_map[label_name]
			self.set_reg_free(label_bool_reg)
			self.reg_map[label_bool_reg] = -1

	def gerar_goto(self, inter):
		self.emitir('jmp', inter[1])

	def gerar_jump_if_false(self, inter):
		bool_reg = self.reg_map[inter[1]]
		label_name = inter[2]

		self.emitir('beq', f'$r{bool_reg},', '$r0,', label_name)
		self.label_map[label_name] = bool_reg

	def gerar_comparacao(self, inter):
		operacao = inter[0]
		operando_1 = inter[1]
		operando_2 = inter[2]
		destino = inter[3]

		reg_1 = self.carregar_operando(operando_1)
		reg_2 = self.carregar_operando(operando_2)

		bool_reg = self.get_free_reg()
		self.set_reg_busy(bool_reg)

		if operacao == 'equal':
			self.emitir('seq', f'$r{bool_reg},', f'$r{reg_1},', f'$r{reg_2}')

		elif operacao == 'not_equal':
			self.emitir('sneq', f'$r{bool_reg},', f'$r{reg_1},', f'$r{reg_2}')

		elif operacao == 'less_than':
			self.emitir('slt', f'$r{bool_reg},', f'$r{reg_1},', f'$r{reg_2}')

		elif operacao == 'greater_than':
			self.emitir('slt', f'$r{bool_reg},', f'$r{reg_2},', f'$r{reg_1}')

		elif operacao == 'less_or_equal_than':
			self.emitir('slet', f'$r{bool_reg},', f'$r{reg_1},', f'$r{reg_2}')

		elif operacao == 'greater_or_equal_than':
			self.emitir('slet', f'$r{bool_reg},', f'$r{reg_2},', f'$r{reg_1}')

		self.reg_map[destino] = bool_reg

		self.liberar_operando(operando_1, reg_1)
		self.liberar_operando(operando_2, reg_2)
	# ==========================================================
	# Argumentos de funções
	# ==========================================================

	def gerar_arg(self, inter):
		function_name = inter[1]
		param = inter[2]

		if function_name == 'output' or function_name == 'UART_output':
			self.preparar_saida(param)
			return

		funcoes_nativas_com_argumentos = [
			'load_os',
			'move_HD_mem',
			'store_HD',
			'move_reg_proc_OS',
			'move_reg_OS_proc',
			'swap_process',
			'write_lcd',
			'concatenate',
			'load_reg_context',
			'store_reg_context',
			'set_proc_pc'
		]

		if function_name in funcoes_nativas_com_argumentos:
			self.source_funct_args.append(param)
			return

		if function_name in self.source_functions:
			return

		reg = self.carregar_parametro(param)

		self.emitir('inc', '$sp')
		self.emitir('push', '$sp,', '0,', f'$r{reg}')

	def preparar_saida(self, param):
		io_reg = 27
		reg = self.carregar_operando(param)

		self.emitir('addi', f'$r{io_reg},', f'$r{reg},', '0')

		self.liberar_operando(param, reg)

	def carregar_parametro(self, param):
		tipo = self.intermediate_tkn_type(param)
		reg = self.get_free_reg()

		if tipo == 'var':
			simbolo = self.obter_simbolo(param)

			if self.get_symbol_id_type(simbolo) == 'var[]':
				arr_ini_position = self.obter_inicio_vetor(param)

				if self.actual_scope == 'main':
					self.emitir('ldi', f'$r{reg},', arr_ini_position)
				else:
					self.emitir('ld', f'$r{reg},', '$r0,', arr_ini_position)
			else:
				self.emitir(
					'ld',
					f'$r{reg},',
					'$r0,',
					self.get_symbol_mem_location(simbolo)
				)

			self.set_reg_busy(reg)
			return reg

		if tipo == 'num':
			self.emitir('ldi', f'$r{reg},', param)
			self.set_reg_busy(reg)
			return reg

		if tipo == 'temp':
			if param in self.array_temp:
				array_val_reg = self.reg_map[param]

				self.emitir('ld', f'$r{reg},', f'$r{array_val_reg},', '0')

				self.set_reg_busy(reg)
				self.set_reg_free(array_val_reg)
				self.reg_map[param] = -1

				return reg

			reg = self.reg_map[param]
			self.reg_map[param] = -1
			return reg

		return reg

	# ==========================================================
	# Declaração de função
	# ==========================================================

	def gerar_function(self, inter):
		function_name = inter[1]

		self.ra_stored[function_name] = True if function_name == 'main' else False
		self.emitir_label(function_name)
		self.actual_scope = function_name

		if function_name != 'main':
			self.desempilhar_parametros(function_name)

		if self.ra_stored[self.actual_scope] is False:
			self.ra_stored[self.actual_scope] = True
			self.emitir('inc', '$sp')
			self.emitir('push', '$sp,', '0,', '$ra')

	def desempilhar_parametros(self, function_name):
		param_list = self.get_symbol_parameters(self.symbol_table[function_name])

		if len(param_list) == 1 and param_list[0] is None:
			return

		aux_reg = self.get_free_reg()

		for param in reversed(param_list):
			self.emitir('pop', f'$r{aux_reg},', '$sp,', 0)
			self.emitir('dec', '$sp')
			self.emitir(
				'str',
				'$r0,',
				str(self.obter_posicao_memoria(param)) + ',',
				f'$r{aux_reg}'
			)
	# ==========================================================
	# Chamadas de função
	# ==========================================================

	def gerar_call(self, inter):
		function_name = inter[1]

		if function_name in self.source_functions:
			self.gerar_call_nativa(inter)
			return

		self.reg_map[inter[3]] = 29
		self.emitir('jal', function_name)

		if function_name == self.actual_scope and self.actual_scope != 'main':
			self.emitir('pop', '$ra,', '$sp,', 0)
			self.emitir('dec', '$sp')

	def gerar_call_nativa(self, inter):
		function_name = inter[1]

		if function_name == 'output':
			self.gerar_call_output()

		elif function_name == 'input':
			self.gerar_call_input(inter)

		elif function_name == 'UART_input':
			self.gerar_call_UART_input(inter)

		elif function_name == 'UART_output':
			self.gerar_call_UART_output()

		elif function_name == 'end_bios':
			self.emitir('btm')

		elif function_name == 'load_os':
			self.gerar_call_tres_argumentos('ldos')

		elif function_name == 'move_HD_mem':
			self.gerar_call_tres_argumentos('mhdm')

		elif function_name == 'store_HD':
			self.gerar_call_tres_argumentos('strhd')

		elif function_name == 'move_reg_OS_proc':
			self.gerar_call_move_reg_OS_proc()

		elif function_name == 'move_reg_proc_OS':
			self.gerar_call_move_reg_proc_OS()

		elif function_name == 'swap_process':
			self.gerar_call_swap_process()

		elif function_name == 'write_lcd':
			self.gerar_call_write_lcd()

		elif function_name == 'concatenate':
			self.gerar_call_concatenate(inter)

		elif function_name == 'get_interruption':
			self.gerar_call_get_interruption(inter)

		elif function_name == 'store_reg_context':
			self.gerar_call_store_reg_context()

		elif function_name == 'load_reg_context':
			self.gerar_call_load_reg_context()

		elif function_name == 'recover_OS':
			self.gerar_call_recover_OS()

		elif function_name == 'get_proc_pc':
			self.gerar_call_get_proc_pc(inter)

		elif function_name == 'set_proc_pc':
			self.gerar_call_set_proc_pc()

	# ==========================================================
	# Input / Output / UART
	# ==========================================================

	def limpar_argumentos_nativos(self):
		self.source_funct_args.clear()

	def gerar_call_output(self):
		io_reg = 27

		if self.mode == 'os':
			self.emitir('out', f'$r{io_reg}')
		else:
			self.emitir('syscall', '1')
			self.emitir('nop')

		self.limpar_argumentos_nativos()

	def gerar_call_input(self, inter):
		if self.mode == 'os':
			reg = self.get_free_reg()
			self.emitir('in', f'$r{reg}')
			self.reg_map[inter[3]] = reg
		else:
			io_reg = 27
			self.emitir('syscall', '0')
			self.emitir('nop')
			self.reg_map[inter[3]] = io_reg

		self.limpar_argumentos_nativos()

	def gerar_call_UART_input(self, inter):
		if self.mode == 'os':
			reg = self.get_free_reg()
			self.emitir('rcv', f'$r{reg}')
			self.reg_map[inter[3]] = reg
		else:
			io_reg = 27
			self.emitir('syscall', '2')
			self.emitir('nop')
			self.reg_map[inter[3]] = io_reg

		self.limpar_argumentos_nativos()

	def gerar_call_UART_output(self):
		if self.mode == 'os':
			io_reg = 27
			self.emitir('send', f'$r{io_reg}')
		else:
			self.emitir('syscall', '3')
			self.emitir('nop')

		self.limpar_argumentos_nativos()
	# ==========================================================
	# HD / BIOS
	# ==========================================================

	def carregar_tres_argumentos_nativos(self):
		regs = []

		for indice in range(3):
			reg = self.get_free_reg()
			self.set_reg_busy(reg)

			self.emitir(
				'ld',
				f'$r{reg},',
				'$r0,',
				self.obter_posicao_memoria(self.source_funct_args[indice])
			)

			regs.append(reg)

		return regs

	def gerar_call_tres_argumentos(self, instrucao):
		reg1, reg2, reg3 = self.carregar_tres_argumentos_nativos()

		self.emitir(instrucao, f'$r{reg1},', f'$r{reg2},', f'$r{reg3}')

		self.set_reg_free(reg1)
		self.set_reg_free(reg2)
		self.set_reg_free(reg3)
		self.limpar_argumentos_nativos()

	# ==========================================================
	# Registradores SO / Processo
	# ==========================================================

	def gerar_call_move_reg_OS_proc(self):
		variable_reg = self.get_free_reg()
		reg_destiny = self.source_funct_args[1]

		self.emitir(
			'ld',
			f'$r{variable_reg},',
			'$r0,',
			f'{self.obter_posicao_memoria(self.source_funct_args[0])}'
		)

		self.emitir('cwsfh')
		self.emitir('add', f'$r{reg_destiny},', f'$r{variable_reg},', '$r0')
		self.emitir('cwsfh')

		self.limpar_argumentos_nativos()

	def gerar_call_move_reg_proc_OS(self):
		reg_destiny = self.get_free_reg()
		reg_source = self.source_funct_args[0]

		self.emitir('crsfh')
		self.emitir('add', f'$r{reg_destiny},', f'$r{reg_source},', '$r0')
		self.emitir('crsfh')

		self.emitir(
			'str',
			'$r0,',
			f'{self.obter_posicao_memoria(self.source_funct_args[1])}',
			f'$r{reg_destiny}'
		)

		self.limpar_argumentos_nativos()

	def gerar_call_swap_process(self):
		proc_num_reg = 25

		self.emitir('nop')
		self.emitir('crsfh')
		self.emitir('cwsfh')

		self.emitir(
			'ld',
			f'$r{proc_num_reg},',
			'$r0,',
			self.obter_posicao_memoria(self.source_funct_args[0])
		)

		self.emitir('sprc', f'$r{proc_num_reg}')
		self.limpar_argumentos_nativos()

	# ==========================================================
	# LCD / concatenação
	# ==========================================================

	def gerar_call_write_lcd(self):
		offset_msg = self.source_funct_args[0]
		self.emitir('cmsg', f'{offset_msg}')
		self.limpar_argumentos_nativos()

	def gerar_call_concatenate(self, inter):
		param_reg_1 = self.get_free_reg()
		self.set_reg_busy(param_reg_1)

		param_reg_2 = self.get_free_reg()
		self.set_reg_busy(param_reg_2)

		self.emitir(
			'ld',
			f'$r{param_reg_1},',
			'$r0,',
			self.obter_posicao_memoria(self.source_funct_args[0])
		)

		self.emitir(
			'ld',
			f'$r{param_reg_2},',
			'$r0,',
			self.obter_posicao_memoria(self.source_funct_args[1])
		)

		return_reg = 29

		self.emitir(
			'conc',
			f'$r{return_reg},',
			f'$r{param_reg_1},',
			f'$r{param_reg_2}'
		)

		self.reg_map[inter[3]] = return_reg
		self.limpar_argumentos_nativos()

	# ==========================================================
	# Interrupção e PC de processo
	# ==========================================================

	def gerar_call_get_interruption(self, inter):
		intrpt_reg = 28
		return_reg = 29

		self.emitir('addi', f'$r{return_reg}', f'$r{intrpt_reg}', '0')
		self.reg_map[inter[3]] = return_reg

		self.limpar_argumentos_nativos()

	def gerar_call_get_proc_pc(self, inter):
		proc_pc_reg = 28
		return_reg = 29

		self.emitir('getpc')
		self.emitir('addi', f'$r{return_reg},', f'$r{proc_pc_reg},', '0')
		self.reg_map[inter[3]] = return_reg

		self.limpar_argumentos_nativos()

	def gerar_call_set_proc_pc(self):
		reg = self.get_free_reg()

		self.emitir(
			'ld',
			f'$r{reg},',
			'$r0,',
			self.obter_posicao_memoria(self.source_funct_args[0])
		)

		self.emitir('setpc', f'$r{reg}')
		self.limpar_argumentos_nativos()
	# ==========================================================
	# Troca de contexto
	# ==========================================================

	def gerar_call_store_reg_context(self):
		param_reg_1 = self.source_funct_args[0]
		self.set_reg_busy(param_reg_1)

		param_reg_2 = self.get_free_reg()
		self.set_reg_busy(param_reg_2)

		param_offs_3 = self.source_funct_args[2]
		aux_reg = self.get_free_reg()

		self.emitir('ld', f'$r{param_reg_2},', '$r0,', self.obter_posicao_memoria(self.source_funct_args[1]))
		self.emitir('addi', f'$r{param_reg_2},', f'$r{param_reg_2},', f'{param_offs_3}')
		self.emitir('crsfh')
		self.emitir('addi', f'$r{aux_reg},', f'$r{param_reg_1},', '0')
		self.emitir('crsfh')
		self.emitir('str', f'$r{param_reg_2},', '0,', f'$r{aux_reg}')

		self.set_reg_free(param_reg_1)
		self.set_reg_free(param_reg_2)
		self.set_reg_free(aux_reg)
		self.limpar_argumentos_nativos()

	def gerar_call_load_reg_context(self):
		param_reg_1 = self.source_funct_args[0]
		self.set_reg_busy(param_reg_1)

		param_reg_2 = self.get_free_reg()
		self.set_reg_busy(param_reg_2)

		param_offs_3 = self.source_funct_args[2]

		self.emitir('ld', f'$r{param_reg_2},', '$r0,', self.obter_posicao_memoria(self.source_funct_args[1]))
		self.emitir('addi', f'$r{param_reg_2}', f'$r{param_reg_2}', f'{param_offs_3}')
		self.emitir('cwsfh')
		self.emitir('ld', f'$r{param_reg_1}', f'$r{param_reg_2}', '0')
		self.emitir('cwsfh')

		self.set_reg_free(param_reg_1)
		self.set_reg_free(param_reg_2)
		self.limpar_argumentos_nativos()

	def gerar_call_recover_OS(self):
		self.emitir('nop')
		self.emitir('crsfh')
		self.emitir('cwsfh')
		self.emitir('nop')
		self.limpar_argumentos_nativos()

	# ==========================================================
	# Return
	# ==========================================================

	def gerar_return(self, inter):
		if self.actual_scope == 'main':
			return

		if self.get_symbol_data_type(self.symbol_table[self.actual_scope]) != 'void':
			self.gerar_valor_retorno(inter[1])

		if self.ra_stored[self.actual_scope] is True:
			self.emitir('pop', '$ra,', '$sp,', 0)
			self.emitir('dec', '$sp')

		self.emitir('jmpr', '$ra')

	def gerar_valor_retorno(self, ret_val):
		reg = 29
		tipo = self.intermediate_tkn_type(ret_val)

		if tipo == 'var':
			self.emitir('ld', f'$r{reg},', '$r0,', self.obter_posicao_memoria(ret_val))

		elif tipo == 'num':
			self.emitir('ldi', f'$r{reg},', ret_val)

		elif tipo == 'temp':
			if ret_val in self.array_temp:
				array_val_reg = self.reg_map[ret_val]
				self.emitir('ld', f'$r{reg},', f'$r{array_val_reg},', '0')
				self.set_reg_free(array_val_reg)
				self.reg_map[ret_val] = -1
			else:
				aux_reg = self.reg_map[ret_val]
				self.reg_map[ret_val] = -1
				self.set_reg_free(aux_reg)
				self.emitir('addi', f'$r{reg},', f'$r{aux_reg},', '0')

	# ==========================================================
	# Síntese principal
	# ==========================================================

	def synthesis(self):
		for inter in self.intermediate_code:
			inter_op = inter[0]

			if inter_op == 'addition':
				self.gerar_addition(inter)

			elif inter_op == 'subtraction':
				self.gerar_subtraction(inter)

			elif inter_op == 'multiplication':
				self.gerar_multiplication(inter)

			elif inter_op == 'division':
				self.gerar_division(inter)

			elif inter_op == 'assign':
				self.gerar_assign(inter)

			elif inter_op == 'weak_assign':
				self.gerar_weak_assign(inter)

			elif inter_op == 'array_assign':
				self.gerar_array_assign(inter)

			elif inter_op == 'label':
				self.gerar_label(inter)

			elif inter_op == 'end_label':
				self.gerar_end_label(inter)

			elif inter_op == 'goto':
				self.gerar_goto(inter)

			elif inter_op in self.comparisons:
				self.gerar_comparacao(inter)

			elif inter_op == 'jump_if_false':
				self.gerar_jump_if_false(inter)

			elif inter_op == 'arg':
				self.gerar_arg(inter)

			elif inter_op == 'function':
				self.gerar_function(inter)

			elif inter_op == 'call':
				self.gerar_call(inter)

			elif inter_op == 'return':
				self.gerar_return(inter)

			else:
				continue
