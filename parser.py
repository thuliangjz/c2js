import ply.yacc as yacc
from scanner import tokens
from classes import para_list, para_item
count_ID = 0


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

#生成函数体
def p_function(p):
    '''function : TYPE ID '(' para_list ')' '{' '}' '''
    p[0] = p[4]

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

def p_expr_group(p):
    '''expression : '(' expression ')' '''
    p[0] = p[1] + p[2] + p[3]

def p_expr_const(p):
    ''' expression : INTEGER
                    | FRACTION '''
    p[0] = p[1]

#TODO:在此检查变量是否已经使用，需要借助当前已声明变量表
def p_expr_id(p):
    ''' expression : ID '''
    p[0] = p[1]

#赋值语句
def p_assign_instr(p):
    '''assigin_instr : ID '=' expression '''


#初始化语句，遇到的id加入局部变量名列表中
def p_init_expr(p):
    ''' init_expr : ID '=' expression
                    | ID '''

def p_init_expr_lst(p):
    '''init_expr_lst : init_expr 
                    | init_expr ',' init_expr_lst '''

def p_init_instr(p):
    '''init_instr : TYPE init_expr_list '''




def p_empty(p):
    '''empty :'''
    pass

parser = yacc.yacc()
result = parser.parse('int Alloha (int a, int b, float c, char d) { } ')
print(result.id_list)






'''
如果需要在函数中使用全局变量，则需要添加global标签

'''