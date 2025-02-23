import argparse
import re
from typing import List, Tuple

# Reserved words
RESERVED_WORDS = {
    'void', 'int', 'double', 'bool',
    'string', 'null', 'for',
    'while', 'if', 'else', 'return',
    'break', 'Print', 'ReadInteger', 'ReadLine'
}

# Define regex patterns for each token type
token_patterns = [
    (r'\b(?:' + '|'.join(RESERVED_WORDS) + r')\b', "T_KEYWORD"),             # Keywords
    (r'\b(true|false)\b', "T_BoolConstant"),                                 # Boolean Constant
    (r'\b[a-zA-Z][a-zA-Z0-9_]{0,30}\b', "identifier"),                       # Identifiers
    (r'0[xX][0-9a-fA-F]+', "hexadecimal integer"),                           # Hexadecimal integers
    (r'\d+\.\d*([eE][+-]?\d+)?', "double constant"),                         # Double constants with exponent
    (r'\d+\.\d*', "double constant"),                                        # Double constants without exponent
    (r'\d+', "decimal integer"),                                             # Decimal integers
    (r'"[^"\n]*"', "T_StringConstant"),                                      # String constants
    (r'<=|>=|==|!=|&&|\|\||[+\-*/%<>=!;,.(){}]', "operator or punctuation"), # Operators and punctuation
    (r'\S+', "T_UNKOWN")                                                     # Unknown tokens
]

# Compile the regex patterns
compiled_patterns = [(re.compile(pattern), token_type) for pattern, token_type in token_patterns]

# Function to tokenize and classify the input
def tokenize(input_string: str) -> List[Tuple[str, str, int, Tuple[int, int]]]:
    tokens = []
    line = 1
    column = 1
    while input_string:
        # Skip leading whitespace and update line/column positions
        if input_string[0].isspace():
            if input_string[0] == '\n':
                line += 1
                column = 1
            else:
                column += 1
            input_string = input_string[1:]
            continue

        # matched = False
        for pattern, token_type in compiled_patterns:
            match = pattern.match(input_string)
            if match:
                token = match.group(0)
                token_length = len(token)
                # Record the token, its type, line, and column range
                tokens.append((token, token_type, line, (column, column + token_length - 1)))
                # Update the column position
                column += token_length
                # Advance the input string
                input_string = input_string[token_length:]
                # matched = True
                break

        # if not matched:
        #     # If no pattern matches, treat the next character as an unknown token
        #     tokens.append((input_string[0], "unknown", line, (column, column)))
        #     column += 1
        #     input_string = input_string[1:]

    return tokens

# Function to read input from a file
def read_input_from_file(filename: str) -> str:
    with open(filename, "r") as file:
        return file.read()

# Main function
def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Tokenize input from a file.")
    parser.add_argument("filename", help="The file containing the input to tokenize.")
    args = parser.parse_args()

    # Read input from the file
    input_string = read_input_from_file(args.filename)

    # Tokenize and classify the input
    tokens = tokenize(input_string)

    # Print tokens with their types
    for token, token_type, line, (start_col, end_col) in tokens:
        #TODO: if for unknown
        #TODO: add values
        #TODO: add parser for things
        # Conditional formatting
        formatted_token = f"{token:<12}" if len(token) < 12 else f"{token} "
        print(f"{formatted_token} line {line} cols {start_col}-{end_col} is {token_type}")

# Run the main function
if __name__ == "__main__":
    main()