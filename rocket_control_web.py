from wsgiref.simple_server import make_server
from SOAPpy import SOAPProxy
from urllib import unquote
import sys
host = "localhost"
port = 51285
if len(sys.argv) > 1:
    host = sys.argv[1]
if len(sys.argv) > 2:
    port = int(sys.argv[2])
server =  SOAPProxy("http://%s:%d" % (host,port))

def rocket_control_app(environ, start_response):
    from StringIO import StringIO
    rockets = eval(server.list_rockets())
    stdout = StringIO()

    stdout.write("<html><body><h1>Rocket Control</h1>\n")
    if environ['REQUEST_METHOD'] == 'POST' :
        size = int(environ['CONTENT_LENGTH'])
        command_str = environ['wsgi.input'].read(size)
        stdout.write(command_str)
        commands = command_str.split("&")
        new_command = unquote(commands[-1].split("=")[-1])
        for command in commands[:-1]:
            name, value = command.split("=")
            if name == "all":
                for rocket in rockets:
                    server.command(rocket, new_command)
            try:
                rocket = int(name) 
                server.command(rocket,new_command)
                print rocket, new_command
            except:
                pass
            
        # for rocket in rockets create heckbox
        # create text field
    stdout.write('<form method="POST">')
    stdout.write('<input type="checkbox" name="all">All<br>\n')
    for rocket in rockets:
        stdout.write('<input type="checkbox" name="%s">Rocket %s<br>\n' % (rocket, rocket))
    stdout.write('Command: <input type="text" name="command" value="fire:1"><br>\n')
    stdout.write('Command: <input type="checkbox" name="fire" value="Fire"><br>\n')

    stdout.write('<input type="submit"></form>\n')

    stdout.write("</body></html>")
    status = b'200 OK' # HTTP Status
    headers = [(b'Content-type', b'text/html; charset=utf-8')] # HTTP Headers
    start_response(status, headers)
    
    # The returned object is going to be printed
    return [stdout.getvalue()]

httpd = make_server('', 8080, rocket_control_app)
print("Serving on port 8080...")

# Serve until process is killed
httpd.serve_forever()
