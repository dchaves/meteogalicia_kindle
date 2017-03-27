#!flask/bin/python
from server import server
server.run(port=5080, debug=True, host='0.0.0.0')
