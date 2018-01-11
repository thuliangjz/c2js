import ply.yacc as yacc
from scanner import tokens, last_type_met
from classes import para_list, para_item, init_item

precedence = (
       ("right", '='),
       ("left", 'OR'),
       ("left", 'AND'),
       ("left", '|'),
       ("left", '^'),
       ("left", '&'),
       ("nonassoc", '<', '>', 'EQ', 'NEQ', 'LE', 'GE'),
       ("left", 'SHL', 'SHR'),
       ("left", '+', '-'),
       ("left", '*', '/', '%'),
)

local_symbol_table = {}
init_type = None    #在初始化变量时进行继承属性模拟求值

def is_defined(name):
    global local_symbol_table
    if not local_symbol_table.get(name):
        raise Exception("value used before defined")

def is_duplicate(name):
    global local_symbol_table
    if local_symbol_table.get(name):
        raise Exception("duplicate variable declearation")

#生成函数体
def p_function(p):
    '''function : TYPE ID '(' para_list ')' new_function_init '{' instruction_list '}' '''
    p[0] = p[4]

def p_new_func(p):
    '''new_function_init : empty'''
    global local_symbol_table
    local_symbol_table.clear()

#参数列表
def p_para_list(p):
    '''para_list : para_item ',' para_list
                    | empty
                    | para_item '''
    a = para_list()
    len_p = len(p)
    if len_p > 1:
        a.id_list.append(p[1])
        if len_p > 2:
            a.id_list.extend(p[3].id_list)
    p[0] = a

def p_para_item(p):
    '''para_item : TYPE ID '''
    a = para_item()
    a.var_type = p[1]
    a.var_name = p[2]
    #参数列表中的元素插入符号表中
    is_duplicate(p[2])
    local_symbol_table[p[2]] = p[1]
    p[0] = a

#各类指令,instruction_list和instruction均为字符串
def p_instr_list(p):
    '''instruction_list : instruction instruction_list
                        | instruction
                        | empty '''
    p[0] = p[1]
    if len(p) > 2:
        p[0] += p[2]

def p_instr(p):
    '''instruction : init_instr
                    | assign_instr
                    | break_instr
                    | return_instr 
                    | for_instr
                    | selection_instr
                    | ';' '''
    p[0] = p[1]

def p_instr_brac(p):
    '''instruction : '{' instruction_list '}' '''
    p[0] = "{%s}"%(p[2])

#表达式定义,包括二元运算符，括号，常量（当前只支持数字）,表达式直接复制字符串即可
def p_expr_binop(p):
    '''expression : expression '+' expression
                    | expression '-' expression
                    | expression '*' expression
                    | expression '/' expression
                    | expression '%' expression
                    | expression '|' expression
                    | expression '&' expression
                    | expression '^' expression
                    | expression AND expression
                    | expression OR expression
                    | expression SHL expression
                    | expression SHR expression
                    | expression EQ expression
                    | expression NEQ expression
                    | expression '>' expression
                    | expression '<' expression
                    | expression LE expression
                    | expression GE expression
                    | expression '=' expression '''
    p[0] = p[1] + p[2] + p[3]

#对++和--运算符的支持
def p_expr_uni(p):
    '''expression : DPLUS ID 
                    | ID DPLUS
                    | DMINUS ID
                    | ID DMINUS'''
    p[0] = p[1] + p[2]

def p_expr_group(p):
    '''expression : '(' expression ')' '''
    p[0] = p[1] + p[2] + p[3]

def p_expr_const(p):
    ''' expression : INTEGER
                    | FRACTION '''
    p[0] = p[1]

#TODO:在expression中支持函数调用结果作为运算对象

def p_expr_id(p):
    ''' expression : ID '''
    is_defined(p[1])
    p[0] = p[1]

#初始化语句，遇到的id加入局部变量名列表中,需要加分号
def p_init_instr(p):
    '''init_instr : TYPE init_expr_list ';' '''
    p[0] = "var "
    global local_symbol_table
    for item in p[2]:
       p[0] += item.code

#为了保证后面的表达式可以直接使用前面定义的变量，on the fly地把定义的变量插入local_symbol_table中,从而需要last_type_met支持
def p_init_expr(p):
    ''' init_expr : ID '=' expression
                    | ID '''
    global local_symbol_table
    #检查变量定义是否重复
    is_duplicate(p[1])
    local_symbol_table[p[1]] = last_type_met
    a = init_item()
    a.code = p[1] + p[2] + p[3] if len(p) == 4 else p[1]
    a.name = p[1]
    p[0] = a


#expr_lst中存的是init_item对象
def p_init_expr_lst(p):
    '''init_expr_list : init_expr 
                    | init_expr ',' init_expr_list '''
    a = []
    a.append(p[1])
    if len(p) > 2:
        p[1].code += ','
        a.extend(p[4])
    p[0] = a



#赋值语句，根据赋值对象的类型对得到的值进行转化，暂时只考虑赋值为整型
def p_assign_instr(p):
    '''assign_instr : ID '=' expression ';' '''
    is_defined(p[1])
    p[0] = p[2] + p[3]
    if local_symbol_table.get(p[1]).s_type == "INT":
        p[0] = "Math.floor(%s)"%(p[0])
    p[0] = "%s%s"%(p[1], p[0])

#跳出循环指令
def p_break_instr(p):
    '''break_instr : BREAK ';' '''
    p[0] = p[1] + ';'

#返回指令
def p_return_instr(p):
    '''return_instr : RETURN expression ';' '''
    p[0] = p[1] + p[2] + ';'

#for 和选择指令支持
def p_for_instr(p):
    ''' for_instr : FOR '(' expression_opt ';' expression_opt ';' expression_opt ')' instruction '''
    p[0] = ''
    for i in range(1, len(p)):
        p[0] += p[i]

def p_selection_instr(p):
    ''' selection_instr : IF '(' expression ')' instruction
                        | IF '(' expression ')' instruction ELSE '(' expression ')' instruction '''
    p[0] = ''
    for i in range(1, len(p)):
        p[0] += p[i]


def p_expr_opt(p):
    ''' expression_opt : expression 
                    | empty '''
    p[0] = p[1]

def p_empty(p):
    '''empty :'''
    pass

parser = yacc.yacc()
result = parser.parse('int Alloha (int a, int b, float c, char d) { } ')
print(result.id_list)






'''
如果需要在函数中使用全局变量，则需要添加global标签
对变量的声明进行了检查,在局部符号表中添加相应变量
根据变量类型进行求值后的转化
对分号进行了检查
instruction变元支持大括号
'''