![REDCap Branching Logic Parser Logo](logo-small.png)

# REDCap Branching Logic Parser

This Python library automatically parses the REDCap platform's branching logic strings. In REDCap, instruments contain fields (i.e. 'variables') which may be displayed conditionally using their *branching logic* parameter. This function is often used to conceal irrelevant questions in an instrument, or to direct (i.e. branch) the question-flow.

Because branching logic serves an important role in the data collection workflow, organisations may need to parse a field's branching logic as a part of an automated data validation routine. For example, organisations may export their REDCap database, and run automated queries using Python that takes into account whether a field is displayed or hidden. The REDCap branching library parser uses `pyparsing` to implement a parser which can parse, substitute, and evaluate branching logic.

## Parsing Process

The `BranchingLogicParser` class implements a parser for REDCap's Branching Logic. It takes a branching logic string as input and produces a boolean output indicating whether the logic is satisfied. The parsing process is as follows:

1. Initialize the branching logic grammar, which returns a pyparsing grammar that defines the parser.
2. Create a list-based abstract syntax tree (AST) from the branching logic string using the grammar.
3. Parse the AST by performing lookups for every field in it, resulting in a simple nested boolean expression.
4. Evaluate the boolean expression and return a single boolean value.

## Documentation

The `BranchingLogicParser` class exposes the following methods:

* `.grammar()`: Initializes the grammar
* `.create_ast(string)`: Creates an AST from the given string
* `.substitute(ast)`: Performs lookups for every field in the AST
* `.evaluate(expression)`: Evaluates the given boolean expression
* `.parse(string)`: Performs all of the above steps on the given string

The `myField` class represents a REDCap field, or variable. It has the following attributes:

* `field`: The name or label of the field in REDCap.
* `event`: An optional string specifying if the field belongs in a different event or instrument.
* `check`: An optional string specifying if the field refers to a value within a checkbox.

When the `BranchingLogicParser`'s `.create_ast(string)` method is called on a valid REDCap branching logic string, the method creates an AST where every REDCap field is instantiated as a `myField` class object that contains its information and metadata.

## Installation Instructions

To be completed.

## Usage Examples.

To be completed. For an interactive example, please see `docs/example.ipynb`. 

## Development Instructions

In order to run the `unittest` unit testing suite, execute the following command at the project root:

```
python -m unittest discover
```