import configparser

config = configparser.ConfigParser()
config.read('config.ini')

mainPin = config['pin']['mainPIN']
adminPin = config['pin']['adminPIN']
exitPin = config['pin']['exitPIN']

print(mainPin)
print(adminPin)
print(exitPin)