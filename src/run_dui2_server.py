# this is a copy / pasted script from a generated build by pip3

import re
import sys
from dui2.only_server import main
if __name__ == '__main__':
    tmp_off = '''
    #consider removing the next line, as this is a C.L.I. app
    sys.argv[0] = re.sub(r'(-script\.pyw|\.exe)?$', '', sys.argv[0])
    sys.exit(main())
    '''


    import cProfile
    cProfile.run('main()')
