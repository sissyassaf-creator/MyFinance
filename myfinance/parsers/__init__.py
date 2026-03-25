from myfinance.parsers.visa import VisaParser
from myfinance.parsers.max_parser import MaxParser

# Maps input folder name → parser instance
PARSER_REGISTRY = {
    'visa-mizrahi': VisaParser(source_label='visa-mizrahi'),
    'diners-el-al': VisaParser(source_label='diners-el-al'),
    'max': MaxParser(),
}
