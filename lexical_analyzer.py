import argparse
import re
from typing import List, Tuple
from enum import Enum

# Reserved words
RESERVED_WORDS = {
    'void', 'int', 'double', 'bool',
    'string', 'null', 'for',
    'while', 'if', 'else', 'return',
    'break', 'Print', 'ReadInteger', 'ReadLine'
}

class TokenType(Enum):
    KEYWORD = "T_Keyword"
    BOOL = "T_BoolConstant"
    IDENTIFIER = "T_Identifier"
    INTEGER = "T_IntConstant"
    DOUBLE = "T_DoubleConstant"
    STRING = "T_StringConstant"
    OPERATOR = "T_Operator"
    UNKNOWN = "T_Unknown"
    TRUNCATED = "T_Truncated"

class ErrorTypes(Enum):
    ident_too_long = "Identifier too long"
    invalid_directive = "Invalid # directive"
    unterminated_string = "Unterminated string constant"
    unrecognized_char = "Unrecognized char"

# Define regex patterns for each token type
token_patterns = [
    (r'#.*', TokenType.UNKNOWN),  # Comments
    (r'\b(?:' + '|'.join(RESERVED_WORDS) + r')\b', TokenType.KEYWORD), # Keywords
    (r'\b(true|false)\b', TokenType.BOOL),                             # Boolean Constant
    (r'\b[a-zA-Z][a-zA-Z0-9_]{0,30}\b', TokenType.IDENTIFIER),         # Identifiers
    (r'0[xX][0-9a-fA-F]+', TokenType.INTEGER),                         # Hexadecimal integers
    (r'\d+\.\d*([eE][+-]?\d+)?', TokenType.DOUBLE),                    # Double constants with exponent
    (r'\d+\.\d*', TokenType.DOUBLE),                                   # Double constants without exponent
    (r'\d+', TokenType.INTEGER),                                       # Decimal integers
    (r'"[^"\n]*"', TokenType.STRING),                                  # String constants
    (r'<=|>=|==|!=|&&|\|\||[+\-*/%<>=!;,.(){}]', TokenType.OPERATOR),  # Operators and punctuation
    (r'"[^"\n]*', TokenType.UNKNOWN),                                  # Unterminated strings
    (r'\S+', TokenType.UNKNOWN)                                        # Unknown tokens
]

error_patterns = [
    (r'[a-zA-Z][a-zA-Z0-9_]*', ErrorTypes.ident_too_long),  #Ident too long error
    (r'"[^"\n]*', ErrorTypes.unterminated_string),          #String without ending "
    (r'#\S+', ErrorTypes.invalid_directive),                #Invalid # directive
    (r'\S', ErrorTypes.unrecognized_char),                  #Unrecognized char
]

# Compile the regex patterns
compiled_patterns = [(re.compile(pattern), token_type) for pattern, token_type in token_patterns]

compiled_errors = [(re.compile(pattern), token_type) for pattern, token_type in error_patterns]

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

        # Handle single-line comments (//)
        if input_string.startswith("//"):
            # Skip to the end of the line
            end_of_line = input_string.find("\n")
            if end_of_line == -1:
                # No newline found, comment extends to the end of the input
                input_string = ""
            else:
                # Skip the comment and the newline
                input_string = input_string[end_of_line + 1:]
                line += 1
                column = 1
            continue

        # Handle multi-line comments (/* ... */)
        if input_string.startswith("/*"):
            # Find the end of the comment
            end_of_comment = input_string.find("*/")
            if end_of_comment == -1:
                # No closing */ found, treat the rest of the input as a comment
                input_string = ""
            else:
                # Skip the comment and update line/column positions
                comment = input_string[:end_of_comment + 2]
                # Count newlines in the comment to update the line number
                newlines = comment.count("\n")
                if newlines > 0:
                    line += newlines
                    # Update column to the position after the comment
                    last_newline = comment.rfind("\n")
                    column = len(comment) - last_newline
                else:
                    column += len(comment)
                # Advance the input string
                input_string = input_string[end_of_comment + 2:]
            continue

        for pattern, token_type in compiled_patterns:
            match = pattern.match(input_string)
            if match:
                token = match.group(0)
                token_length = len(token)
                # Record the token, its type, line, and column range
                tokens.append((token, token_type, line, (column, column + token_length - 1)))
                
                #add truncating variable thingy
                if token_type == TokenType.UNKNOWN and token_length > 31:
                    ident_pattern, ident_type = compiled_patterns[3]
                    extra_match = ident_pattern.match(token[:31])
                    if extra_match:
                        tokens.append((token, TokenType.TRUNCATED, line, (column, column + token_length - 1)))

                # Update the column position
                column += token_length
                # Advance the input string
                input_string = input_string[token_length:]
                break

    return tokens

# Function to read input from a file
def read_input_from_file(filename: str) -> str:
    with open(filename, "r") as file:
        return file.read()

def format_token_type(token: str, token_type: Enum) -> str:
    if token_type == TokenType.KEYWORD:
        return f"T_{token[0:1].capitalize()}{token[1:]}"
    
    if token_type == TokenType.OPERATOR:
        if token == "<=":
            return "T_LessEqual"
        elif token == ">=":
            return "T_GreaterEqual"
        elif token == "==":
            return "T_Equal"
        elif token == "!=":
            return "T_NotEqual"
        elif token == "&&":
            return "T_And"
        elif token == "||":
            return "T_Or"
        else:
            return f"\'{token}\'"
        
    if token_type == TokenType.TRUNCATED:
        return TokenType.IDENTIFIER.value
    
    return token_type.value

def translate_to_number(s: str) -> str:
    # Check if the string is a hexadecimal number (starts with '0x' or '0X')
    if s.lower().startswith(('0x', '0X')):
        # Convert the hexadecimal string to a decimal integer
        decimal_value = int(s, 16)
        # Convert the integer to a string
        s = str(decimal_value)
    
    # Check if there is a '.' in the string
    if '.' in s:
        # Split into the part before and after the '.'
        before_decimal, after_decimal = s.split('.', 1)
        # Strip all leading zeros except one if there are any
        if before_decimal.startswith('0'):
            before_decimal = '0' + before_decimal.lstrip('0')
        # Reconstruct the string
        s = before_decimal + '.' + after_decimal
    else:
        # If there is no '.', strip all leading zeros
        s = s.lstrip('0')
        # If all characters were stripped and it's empty, keep at least one '0'
        if not s:
            s = '0'
    
    # Check if 'E' is in the string
    if 'E' in s:
        # Split the string into the number part and the exponent part
        num_part, exp_part = s.split('E')
        
        # Remove any leading '+' in the exponent part
        exp_part = exp_part.lstrip('+')
        
        # Convert the exponent to an integer
        exponent = int(exp_part)
        
        # Handle the case where the number part ends with a dot
        if num_part.endswith('.'):
            num_part = num_part[:-1]
        
        # Split the number into integer and fractional parts
        if '.' in num_part:
            integer_part, fractional_part = num_part.split('.')
        else:
            integer_part, fractional_part = num_part, ''
        
        # Calculate the total number of digits to move the decimal point
        total_digits = len(fractional_part)
        
        # Adjust the integer and fractional parts based on the exponent
        if exponent > 0:
            # Move the decimal point to the right
            if exponent <= total_digits:
                integer_part += fractional_part[:exponent]
                fractional_part = fractional_part[exponent:]
            else:
                integer_part += fractional_part
                fractional_part = ''
                integer_part += '0' * (exponent - total_digits)
        elif exponent < 0:
            # Move the decimal point to the left
            exponent = abs(exponent)
            if exponent <= len(integer_part):
                fractional_part = integer_part[-exponent:] + fractional_part
                integer_part = integer_part[:-exponent]
            else:
                fractional_part = '0' * (exponent - len(integer_part)) + integer_part + fractional_part
                integer_part = ''
        
        # Combine the integer and fractional parts
        result = integer_part + fractional_part
    
    else:
        # If there is no 'E', just return the stripped string
        result = s
    
    return result


def create_token_value(token: str, token_type: TokenType) -> str:   
    if token_type in [TokenType.BOOL, TokenType.INTEGER, 
                      TokenType.DOUBLE, TokenType.STRING]:
        if token_type in [TokenType.INTEGER, TokenType.DOUBLE]:
            token = translate_to_number(token)
        return f" (value = {token})"
    elif token_type == TokenType.TRUNCATED:
        return f" (truncated to {token[:31]})"
    
    return " "

def detect_error(token: str) -> str:
    for pattern, token_type in compiled_errors:
        match = pattern.match(token)
        if match:
            if token_type == ErrorTypes.invalid_directive:
                return f"*** {token_type.value}"
            elif token_type == ErrorTypes.ident_too_long:
                return f"*** {token_type.value}: \"{token}\""
            elif token_type == ErrorTypes.unrecognized_char:
                return f"*** {token_type.value}: \'{token}\'"
            else:
                return f"*** {token_type.value}: {token}"

    return f"*** Unreconized error: {token}"

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
        if token_type == TokenType.UNKNOWN:
            print()
            print(f"*** Error line {line}.")
            print(detect_error(token))
            print()
        else:
            # Conditional formatting
            formatted_token = f"{token:<12}" if len(token) < 12 else f"{token}"
            formatted_token_type = format_token_type(token=token, token_type=token_type)
            token_value = create_token_value(token=token, token_type=token_type)
            print(f"{formatted_token} line {line} cols {start_col}-{end_col} is {formatted_token_type}{token_value}")

# Run the main function
if __name__ == "__main__":
    main()