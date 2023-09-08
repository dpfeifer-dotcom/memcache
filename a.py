from server import Client
from utils import Timer

c = Client('192.168.56.1', 6000)

a = c.SET("BBB", 123123)
print(a.error, a.value)

t = Timer()

get = c.GET('BBB')

print('GET - ERR:', get.error, 'VALUE:', get.value)
mod = c.MOD("BBB", 123)
print('MOD - ERR:', mod.error, 'VALUE:', mod.value)
get = c.GET('BBB')
print('GET - ERR:', get.error, 'VALUE:', get.value)
delete = c.DEL('BBB1')
print('DELETE - ERR:', delete.error, 'VALUE:',delete.value)
setexp = c.SETEXP('BBB', 1000)
print('SETEXP - ERR:', setexp.error, 'VALUE:',setexp.value)
getexp = c.GETEXP('BBB')
print('GETEXP - ERR:', getexp.error, 'VALUE:',getexp.value)
pop = c.POP('BBB')
print('POP - ERR:', pop.error, 'VALUE:',pop.value)
getexp = c.GETEXP('BBB')
print('GETEXP - ERR:', getexp.error, 'VALUE:',getexp.value)
keys = c.KEYS()
print('KEYS - ERR:', keys.error, 'VALUE:',keys.value)
lenght = c.LEN()
print('LEN - ERR:', lenght.error, 'VALUE:',lenght.value)
print(t.elaped_time())