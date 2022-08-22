from yandex import yandex_run
from excel import parse_excel
from allright import parse_allright

try:
    parse_excel()
except Exception as e:
    print(f'Private {e}')
try:
    yandex_run()
except Exception as e:
    print(f'Yandex {e}')
try:
    parse_allright()
except Exception as e:
    print(f'Allright {e}')
