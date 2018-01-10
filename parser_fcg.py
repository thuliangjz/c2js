def p_for_instr(p):
    ''' for_instr: FOR '(' expression_opt ';' expression_opt ';' expression_opt ')' '{' instruction_list '}'
                 | FOR '(' expression_opt ';' expression_opt ';' expression_opt ')' instruction '''

def p_selection_instr(p):
    ''' selection_instr : IF '(' expression ')' '{' instruction_list '}' ELSE '{' instruction_list '}' 
                        | IF '(' expression ')' '{' instruction_list '}' ELSE instruction 
                        | IF '(' expression ')' '{' instruction_list '}'   
                        | IF '(' expression ')' instruction ELSE '{' instruction_list '}' 
                        | IF '(' expression ')' instruction ELSE instruction
                        | IF '(' expression ')' instruction'''

def p_expr_opt(p):
    ''' expression_opt : expression | empty '''
