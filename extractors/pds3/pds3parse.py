#! /usr/bin/env python3

import ply.yacc as yacc

from pds3tokens import tokens
import pds3lex

import sys
import json

def p_label(p):
  'label : statements END'
  p[0] = p[1]
  
def p_statements(p):
  '''statements : statements statement
                | statement'''
  if len(p) > 2:
    p[0] = p[1] + [p[2]]
  else:
    p[0] = [p[1]]
                    
  
def p_statement(p):
  '''statement : attribute_statement
              | pointer_statement
              | object_statement
              | group_statement'''
  p[0] = p[1]
                
def p_assignment_statement(p):
  'attribute_statement : IDENT EQUALS value'
  p[0] = {'type':'attribute', 'name':p[1], 'value':p[3]}
  
def p_pointer_statement(p):
  'pointer_statement : POINTER IDENT EQUALS value'
  p[0] = {'type':'pointer', 'name': '^' + p[2], 'value': p[4]}
  
def p_object_statement(p):
  'object_statement : OBJECT EQUALS IDENT statements END_OBJECT EQUALS IDENT'
  p[0] = {'type':'object', 'name': p[3], 'value': p[4]}
  
def p_group_statement(p):
  'group_statement : GROUP EQUALS IDENT statements END_GROUP EQUALS IDENT'
  p[0] = {'type':'group', 'name': p[3], 'value': p[4]}
  
def p_value(p):
  '''value : scalar_value
           | sequence_value
           | set_value'''
  p[0] = p[1]
           
def p_scalar_value(p):
  '''scalar_value : numeric_value
                  | date_time_val
                  | text_string_value
                  | symbol_value'''
  p[0] = p[1]
                  
def p_numeric_value(p):
  '''numeric_value : INTEGER optional_units_expression
                   | BASED_INT optional_units_expression
                   | REAL optional_units_expression'''
  if (p[2]):
    p[0] = {"scalar": p[1], "unit": p[2] }
  else:
    p[0] = {"scalar": p[1]}
                  
def p_optional_units_expression(p):
  '''optional_units_expression : 
                               | units_expression'''
  if (len(p) > 1):
    p[0] = p[1]
  
def p_units_expression(p):
  '''units_expression : L_ANGLE units_factor R_ANGLE
                      | L_ANGLE units_factor mult_op units_factor R_ANGLE '''
  if (len(p) > 6):
    p[0] = p[2] + p[3] + p[4]
  else:
    p[0] = p[2]
                      
def p_units_factor(p):
  '''units_factor : IDENT 
                  | IDENT EXPONENT INTEGER'''
  if (len(p) > 3):
    p[0] = p[1] + [2] + p[3]
  else:
    p[0] = p[1]
  
def p_mult_op(p):
  '''mult_op : MULTIPLY 
            | DIVIDE'''
  p[0] = p[1]  
  
def p_date_time_val(p):
  '''date_time_val : DATE_TIME_VAL'''
  p[0] = {"scalar": p[1]}
  
  
def p_text_string_value(p):
  '''text_string_value : STRING'''
  p[0] = {"scalar": p[1]}
  
def p_symbol_value(p):
  '''symbol_value : IDENT 
                  | SYMBOL'''
  p[0] = {"scalar": p[1]}
    
def p_sequence_value(p):
  '''sequence_value : sequence_1d 
                  | sequence_2d'''
  p[0] = p[1]
    
def p_sequence_1d(p):
  'sequence_1d : L_PAREN scalar_values R_PAREN'
  p[0] = p[1]
  
def p_scalar_values(p):
  '''scalar_values : scalar_value 
                   | scalar_values SEPARATOR scalar_value'''
  if (len(p) > 3):
    p[0] = p[1] + [p[3]]
  else:
    p[0] + [p[1]]
  
def p_sequence_2d(p):
  'sequence_2d : L_PAREN sequence_1ds R_PAREN'
  
def p_sequence_1ds(p):
  '''sequence_1ds : sequence_1d 
                  | sequence_1ds SEPARATOR sequence_1d'''
  
def p_set_value(p):
  'set_value : L_BRACE scalar_values R_BRACE'
  
def p_error(p):
  print('syntax_error: %s' % p.lineno)
  print(p)
  
#parser = yacc.yacc()

def do_parse(data):
  parser = yacc.yacc()
  return parser.parse(data, lexer=pds3lex.lexer)
  
def main(argv=None):
  if argv is None:
    argv = sys.argv
  
  with open(argv[1]) as f:
    data = f.read()
    print(data)
    result = do_parse(data) #parser.parse(data)
    print(json.dumps(result))
  
if __name__ == '__main__':
  sys.exit(main())