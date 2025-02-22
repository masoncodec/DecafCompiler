import argparse
import re

# Reserved words
RESERVED_WORDS = {
    'void', 'int', 'double', 'bool',
    'string', 'null', 'for',
    'while', 'if', 'else', 'return',
    'break', 'Print', 'ReadInteger', 'ReadLine'
}

# # Regular expressions for token patterns
# TOKEN_PATTERNS = [
    # (r'^(' + '|'.join(RESERVED_WORDS) + r')$'),  # Keywords
#     (r'^[A-Za-z]{1}[A-za-z0-9_]{,30}$'),  # Identifiers
#     (r'^(true|false)$'), # Boolean constant
#     ()
# ]

# Define regex patterns for each token type
token_patterns = [
    (r'\b(?:' + '|'.join(RESERVED_WORDS) + r')\b', "reserved word"),        # Reserved words
    (r'\b[a-zA-Z][a-zA-Z0-9_]{0,30}\b', "identifier"),                      # Identifiers
    (r'0[xX][0-9a-fA-F]+', "hexadecimal integer"),                          # Hexadecimal integers
    (r'\d+\.\d*([eE][+-]?\d+)?', "double constant"),                        # Double constants with exponent
    (r'\d+\.\d*', "double constant"),                                       # Double constants without exponent
    (r'\d+', "decimal integer"),                                            # Decimal integers
    (r'"[^"\n]*"', "string constant"),                                      # String constants
    (r'<=|>=|==|!=|&&|\|\||[+-*/%<>=!;,.(){}]', "operator or punctuation"), # Operators and punctuation
    (r'\S+', "unknown")                                                     # Unknown tokens
]