import ply.yacc as yacc
from scanner import tokens
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

def is_defined(name):
    global local_symbol_table
    if not local_symbol_table.get(name):
        raise Exception("value used before defined")

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

#各类指令
def p_instr_list(p):
    '''instruction_list: instruction instruction_list
                        | instruction'''
    p[0] = p[1]
    if len(p) > 2
        p[0] += p[2]

def p_instr(p):
    '''instruction: init_instr
                    | assign_instr
                    | break_instr
                    | return_instr '''

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

#TODO:在此检查变量是否已经使用，需要借助当前已声明变量表
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
        if local_symbol_table.get(item.name):
            raise Exception("duplicate variable name")
        p[0] += item.code

def p_init_expr(p):
    ''' init_expr : ID '=' expression
                    | ID '''
    a = init_item()
    a.code = p[1] + p[2] + p[3] if len(p) == 4 else p[1]
    a.name = p[1]
    p[0] = a

def p_init_expr_lst(p):
    '''init_expr_lst : init_expr 
                    | init_expr ',' init_expr_lst '''
    a = []
    a.append(p[1])
    if len(p) > 2:
        p[1].code += ','
        a.extend(p[4])
    p[0] = a



#赋值语句，根据赋值对象的类型对得到的值进行转化，暂时只考虑赋值为整型
def p_assign_instr(p):
    '''assigin_instr : ID '=' expression ';' '''
    is_defined(p[1])
    p[0] =  p[1] + p[2] + p[3]
    if local_symbol_table.get(p[1]).s_type == "INT":
        p[0] = "Math.floor(%s)"%(p[0])

#跳出循环指令
def p_break_instr(p):
    '''break_instr : BREAK ';' '''
    p[0] = p[1] + ';'

#返回指令
def p_return_instr(p):
    '''return_instr : RETURN expression ';' '''
    p[0] = p[1] + p[2] + ';'

def p_empty(p):
    '''empty :'''
    pass

parser = yacc.yacc()
result = parser.parse('int Alloha (int a, int b, float c, char d) { } ')
print(result.id_list)






'''
如果需要在函数中使用全局变量，则需要添加global标签
对变量的声明进行了检查
根据变量类型进行求值后的转化
对分号进行了检查
'''