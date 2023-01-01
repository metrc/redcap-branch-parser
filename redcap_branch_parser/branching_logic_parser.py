#!/usr/bin/env python3

import pyparsing as pp
import operator as op
from typing import Union

class myField:
    """
    This class represents a REDCap field (i.e. variable).

    field : str
        The name or label of the field in REDCap
    event : Optional[Union[str, None]]
        Specifies if the field belongs in a different event or instrument.
    check : Optional[Union[str, None]]
        Specifies if the field refers to a value within a checkbox
    """
    def __init__(self, field: str, event: Union[str, None] = None, check: Union[str, None] = None) -> None:
        self.field: str = field
        self.event: Union[str, None] = event
        self.check: Union[str, None] = check
    
    def __str__(self) -> str:
        if self.event:
            event_string: str = f"[{self.event}]"
        else:
            event_string: str = ""
        if self.check:
            field_string: str = f"[{self.field}({self.check})]"
        else:
            field_string: str = f"[{self.field}]"

        return f"{event_string}{field_string}"

    def __repr__ (self) -> str:
        return f"myField({self.field}, event={self.event}, check={self.check})"

class BranchingLogicParser:
    """
    This class implements a parser for REDCap's Branching Logic. The overall structure of
    the parsing process is as follows:

    Parsing Process:
        1. Initialise branching logic grammar.
           This returns a pyparsing grammar that defines a parser which yields an AST.
        2. Create list-based abstract-syntax tree (AST) from Branching Logic String
           Using the grammar, parse the given string to yield a list of REDCap Field objects.
        3. Parse list-based AST by performing lookups for every field in the AST.
           This yields a simple nested boolean expression.
        4. Evaluate the resulting list-based boolean expression.
           Now we evaluate the resulting boolean expression and return a single boolean value.

    In __init__(), the class exposes the various user-facing methods that can be used:
        self.grammar    = Initialises the grammar
        self.create_ast = Creates ast from str
        self.substitute = Lookup values from ast
        self.evaluate   = Evaluates boolean expression
        self.parse      = Does all of above.

    The main user-facing methods will be BranchingLogicParser.parse()
    """
    def __create_my_field(self, s: str, loc: int, tokens: pp.ParseResults):
        """
        Private method creates a myField object corresponding to a regular REDCap field
        """
        return myField(tokens[0])

    def __create_my_event_field(self, s: str, loc: int, tokens: pp.ParseResults):
        """
        Private method creates a myField object corresponding to a REDCap field in event
        """
        return myField(tokens[1], event=tokens[0])

    def __create_my_check(self, s: str, loc: int, tokens: pp.ParseResults):
        """
        Private method creates a myField object corresponding to a REDCap field checkbox
        """
        return myField(tokens[0], event=None, check=tokens[1])

    def __create_my_event_check(self, s: str, loc: int, tokens: pp.ParseResults):
        """
        Private method creates a myField object corresponding to REDCap field checkbox in event
        """
        return myField(tokens[1], event=tokens[0], check=tokens[2])

    def __redcap_branching_logic_grammar(self):
        """
        This method creates a parser for the REDCap Branching Logic.
        The grammar for the REDCap Branching logic in Backus-Naur Form (BNF) is defined as follows:
        
            expression ::=  atom [ operator atom ]*
            atom       ::=  variable | value | checkbox | event | varcheck_in_event | variable_in_event | variable_in_check
            operator   ::=  "=" | "<>" | ">" | ">=" | "<" | "<="
            variable   ::=  "[" alphabet "]"
            checkbox   ::=  "(" alphabet ")"
            event      ::=  "[" alphabet "]"
            value      ::=  "'" .*? "'" | '"' .*? '"'
            varcheck_in_event ::= event variable_in_check
            variable_in_event ::= event variable
            variable_in_check ::= "[" alphabet checkbox "]"
        
        The expression is evaluated using infix notation, with the following operator precedence:
            1. "!" (not)
            2. "=" | "<>" | ">" | ">=" | "<" | "<=" (comparison)
            3. "AND"
            4. "OR"
        """
        # Define the alphabet of our grammar
        alphabet = pp.Word(pp.alphanums + "_")
        lbrace = pp.Suppress(pp.Literal('['))
        rbrace = pp.Suppress(pp.Literal(']'))

        # Define the verbs (i.e. operators) of our grammar
        operator = pp.oneOf(("=", "<>", ">", ">=", "<", "<=")).set_results_name("operator")
        and_ = pp.CaselessKeyword("AND").set_results_name("bool")
        or_  = pp.CaselessKeyword("OR").set_results_name("bool")
        not_ = pp.Keyword("!").set_results_name("bool")

        # Now we define the variables
        variable = pp.QuotedString(quote_char="[", end_quote_char="]").set_results_name("variable").set_parse_action(self.__create_my_field)
        
        checkbox = pp.QuotedString(quote_char="(", end_quote_char=")").set_results_name("checkbox")
        event    = pp.QuotedString(quote_char="[", end_quote_char="]").set_results_name("event")
        value    = (pp.QuotedString(quoteChar='"') | pp.QuotedString(quoteChar="'")).set_results_name("value")

        # REDCap Checkbox events
        variable_in_check = (lbrace + alphabet.set_results_name("variable_checkbox") + checkbox + rbrace).set_parse_action(self.__create_my_check)
        variable_in_event = (event + pp.QuotedString(quote_char="[", end_quote_char="]")).set_parse_action(self.__create_my_event_field)


        varcheck_in_event = (event + (lbrace + alphabet.set_results_name("variable_checkbox") + checkbox + rbrace)).set_parse_action(self.__create_my_event_check)

        # The expression
        field = ( varcheck_in_event | variable_in_event | variable_in_check | variable | value)
        expression = pp.Group(field + operator + value).set_results_name("expression", list_all_matches=True)

        # Define the syntax as infix notation, using variables and operators
        redcap_branching_logic_grammar = pp.infix_notation(
            expression,
            # Define operator list, number of terms, and associativity
            [
                (not_, 1, pp.opAssoc.RIGHT),
                (operator, 2, pp.opAssoc.LEFT),
                (and_, 2, pp.opAssoc.LEFT),
                (or_,  2, pp.opAssoc.LEFT),
            ]
        )
        return redcap_branching_logic_grammar

    def __create_ast_as_list(self, input_string: str):
        return self.grammar.parse_string(input_string).as_list()

    def __redcap_lookup(self, field_name: str, data_df) -> str:
        """
        Looks up the value from REDCAP
        """

        return str(data_df[str(field_name)])

    def __field_value_lookup(self, results, data_df):
        scratch = []
        op_lookup = {
            '=' : op.eq,
            "<>": op.ne,
            '<' : op.lt,
            ">" : op.gt,
            '<=': op.le,
            '>=': op.ge
        }

        for index, result in enumerate(results):
            # If the result is a list, we need to recursively evaluate it
            if isinstance(result, list):
                # The recursive evaluation
                inner_layer = self.__field_value_lookup(result, data_df)

                # If it is a simple boolean value, append just the value
                if len(inner_layer) == 1:
                    scratch.append(inner_layer[0])
                else:
                    # Otherwise append the nested list
                    scratch.append(inner_layer)

            elif isinstance(result, myField):
                # Lookup field and evaluate
                field_name = result.field
                operator = op_lookup[results[index + 1]]
                expected = results[index + 2]

                field_value = self.__redcap_lookup(field_name, data_df) # Placeholder
                field_result = operator(field_value, expected)

                print(f"[{field_name}]  {results[index + 1]} {expected}")
                print(f"{field_value} {results[index + 1]} {expected}")

                # Return value
                scratch.append(field_result)
                return scratch

            elif result in ['AND', 'OR']:
                scratch.append(result)
        
        return scratch

    def __boolean_expr_evaluate(self, expr: list) -> bool:
        """
        Traverse a list of boolean expressions and evaluate them.

        Expected input is a list with boolean values, string boolean operators, and nested lists.
        Boolean values and nested lists will be evaluated recursively. String boolean operators will be
        mapped to their corresponding Python boolean functions and used to evaluate the boolean values.
        The final result will be returned as a boolean value.

        Args:
            expr (list): A list of boolean values, string boolean operators, and/or nested lists.
        Returns:
            bool: The final result of evaluating the boolean expressions in the input list.
        """
        # First, we map our boolean operator strings to Python functions
        op_lookup = { 'AND': op.and_, 'OR': op.or_ }
        stack: list[bool] = []
        # Infix holds the boolean operator that will be used
        infix = None

        # For every item in the expr
        for x in expr:
            # If bool, add to stack
            if isinstance(x, bool):
                stack.append(x)
            # If it is a nested list, evaluate the list recursively
            elif isinstance(x, list):
                stack.append(self.__boolean_expr_evaluate(x))
            # But if it is an operator, lookup the Python function
            elif isinstance(x, str):
                infix = op_lookup[x]
                continue # this is necessary so we don't go into infix part
            # And now evaluate the boolean stack with the operator
            if infix:
                left  :bool  = stack.pop()
                right :bool  = stack.pop()
                result:bool = infix(left, right)
                stack.append(result)
                infix = None
                
        return stack[0]

    def __parse(self, input_string: str):
        ast_as_list  = self.__create_ast_as_list(input_string)
        boolean_expr = self.__field_value_lookup(ast_as_list)
        expr_result  = self.__boolean_expr_evaluate(boolean_expr)

        return expr_result

    def __init__(self) -> None:
        """
        Initialise class instance
        """
        self.grammar    = self.__redcap_branching_logic_grammar()
        self.create_ast = self.__create_ast_as_list
        self.substitute = self.__field_value_lookup
        self.evaluate   = self.__boolean_expr_evaluate
        self.parse      = self.__parse

    def print_ast(self, parse_results, depth=0) -> None:
        """
        Print the abstract syntax tree (AST) for the given parse results.
        This function recursively traverses the parse results and prints the
        contents of each `ParseResults` object and token.

        Parameters:
        - parse_results (pyparsing.ParseResults): The parse results object to print.
        - depth (int, optional): The current depth of the recursive traversal. Default is 0.
        """
        for index, result in enumerate(parse_results):
            if isinstance(result, pp.ParseResults):
                print("    " * depth, depth, index, "ParseResult", result.as_list())
                print("    " * depth, ".", ".", "...... Dict", result.as_dict())
                self.print_ast(result, depth=depth+1)
            else:
                print("    " * depth, depth, index, "Token", result)
            