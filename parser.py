import ply.yacc as yacc
from scanner import tokens, last_type_met
from classes import para_list, para_item, init_item, symbol
import scanner

precedence = (
        ("left", ','),
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

local_symbol_table = {} #保存的是symbol对象
init_type = None    #在初始化变量时进行继承属性模拟求值
last_obj_name = None

def is_defined(name):
    global local_symbol_table
    if not local_symbol_table.get(name):
        raise Exception("value used before defined")

def is_duplicate(name):
    global local_symbol_table
    if local_symbol_table.get(name):
        raise Exception("duplicate variable declearation")

def is_ptr(name):
    global local_symbol_table
    s = local_symbol_table.get(name)
    if not s or not s.var_is_ptr:
        raise Exception("not pointer")

def code_concat(p):
    p[0] = ""
    for i in range(1, len(p)):
        if(p[i]):
            p[0] += p[i]

#生成函数体
def p_function(p):
    '''function : TYPE ID new_function_init '(' para_list ')' '{' instruction_list '}' '''
    para_list = p[5]

    p[0] = 'function %s (%s) {%s}'%(p[2],','.join([i.var_name for i in p[5]]) , p[8])

def p_new_func(p):
    '''new_function_init : empty'''
    global local_symbol_table
    local_symbol_table.clear()

#参数列表, 参数存放在一个列表中，每个对象为一个symbol
def p_para_list(p):
    '''para_list : para_item ',' para_list
                    | empty
                    | para_item '''
    a = []
    len_p = len(p)
    if p[1]:
        a.append(p[1])
        if len_p > 2:
            a.extend(p[3])
    p[0] = a

def p_para_item(p):
    '''para_item : TYPE ID
                | TYPE '*' ID '''
    a = symbol()
    a.var_type = p[1]
    a.var_name = p[2] if len(p) == 3 else p[3]
    a.var_is_ptr = len(p) > 3   #如果包含*则为指针类型
    #参数列表中的元素插入符号表中
    is_duplicate(a.var_name)
    local_symbol_table[a.var_name] = a
    p[0] = a

#各类指令,instruction_list和instruction均为字符串
def p_instr_list(p):
    '''instruction_list : instruction instruction_list
                        | instruction
                        | empty '''
    code_concat(p)

def p_instr(p):
    '''instruction : init_instr
                    | assign_instr
                    | break_instr
                    | return_instr 
                    | for_instr
                    | selection_instr
                    | ';' '''
    code_concat(p)

def p_instr_brac(p):
    '''instruction : '{' instruction_list '}' '''
    code_concat(p)

#初始化语句，遇到的id加入局部变量名列表中,需要加分号
def p_init_instr(p):
    '''init_instr : TYPE init_expr_list ';' '''
    p[0] = "var %s;"%(p[2])

#expr_lst中存的是init_expr生成的代码的表
def p_init_expr_lst(p):
    '''init_expr_list : init_expr 
                    | init_expr ',' init_expr_list '''
    code_concat(p)

#由于可能出现赋值，需要对赋值情形做类似assign的处理
def p_init_expr(p):
    ''' init_expr : name_def '=' expression
                    | name_def '''
    if local_symbol_table.get(p[1]).var_type == "INT" and len(p) > 2:
        p[0] = "%s=Math.floor(%s)"%(p[1],p[3])
    else:
        code_concat(p)

#为了保证后面的表达式可以直接使用前面定义的变量，on the fly地把定义的变量插入local_symbol_table中,从而需要last_type_met支持
def p_name_def(p):
    ''' name_def : ID
                | '*' ID '''
    global local_symbol_table
    #检查变量定义是否重复
    a = symbol()
    a.var_name = p[1] if len(p) == 2 else p[2]
    is_duplicate(a.var_name)
    a.var_type = scanner.last_type_met
    a.var_is_ptr = len(p) == 3 
    local_symbol_table[a.var_name] = a
    p[0] = a.var_name

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
                    | expression '=' expression
                    | expression ',' expression '''
    p[0] = p[1] + p[2] + p[3]

#对++和--运算符的支持
def p_expr_uni(p):
    '''expression : DPLUS  real_object
                    | real_object DPLUS
                    | DMINUS real_object
                    | real_object DMINUS'''
    code_concat(p)

def p_expr_group(p):
    '''expression : '(' expression ')' '''
    code_concat(p)

def p_expr_const(p):
    ''' expression : INTEGER
                    | FRACTION '''
    p[0] = p[1]

#TODO:在expression中支持函数调用结果作为运算对象
def p_expr_atomic(p):
    ''' expression : real_object '''
    code_concat(p)

def p_real_object(p):
    ''' real_object : ID
                    | ID '[' expression ']' '''
    is_defined(p[1])
    if len(p) > 2:
        is_ptr(p[1])
    global last_obj_name
    last_obj_name = p[1]
    code_concat(p)


#赋值语句，根据赋值对象的类型对得到的值进行转化，暂时只考虑赋值为整型
def p_assign_instr(p):
    '''assign_instr : real_object get_object_name '=' expression ';' '''
    if local_symbol_table.get(p[2]).var_type == "int":
        p[0] = "%s=Math.floor(%s);"%(p[1],p[4])
    else:
        p[0] = p[1] + p[3] + p[4] + p[5]

def p_get_object_name(p):
    '''get_object_name : empty'''
    p[0] = last_obj_name

#跳出循环指令
def p_break_instr(p):
    '''break_instr : BREAK ';' '''
    p[0] = p[1] + ';'

#返回指令
def p_return_instr(p):
    '''return_instr : RETURN expression ';' '''
    p[0] = p[1]  + ' ' + p[2] + ';'

#for 和选择指令支持
def p_for_instr(p):
    ''' for_instr : FOR '(' expression_opt ';' expression_opt ';' expression_opt ')' instruction '''
    code_concat(p)

def p_selection_instr(p):
    ''' selection_instr : IF '(' expression ')' instruction
                        | IF '(' expression ')' instruction ELSE '(' expression ')' instruction '''
    code_concat(p)


def p_expr_opt(p):
    ''' expression_opt : expression 
                    | empty '''
    p[0] = p[1]

def p_empty(p):
    '''empty :'''
    pass

para_list_test = 'int Alloha (int a, int* b, float c, char d) { } '
init_instr_test = 'int Alloha(){\
    int * p, w;\
    p[1 + w] = 3/2;}'

parlindrome_test = 'int parlindrome (char* str, int len){\
        int tmp, i;\
        tmp = len / 2;\
        for(i = 0; i < tmp; ++i){\
            if(str[i] != str[len - 1 - i])\
                    return 0;\
        }\
        return 1;}'

parser = yacc.yacc()
result = parser.parse(parlindrome_test)
print(result)




'''
如果需要在函数中使用全局变量，则需要添加global标签
对变量的声明进行了检查,在局部符号表中添加相应变量
根据变量类型进行求值后的转化
对分号进行了检查
instruction变元支持大括号
支持数组元素访问和求值
'''