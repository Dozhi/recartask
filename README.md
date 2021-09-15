# recartask
task given by recar 

## How to start

To install env
```sh
python3 -m venv env
source env/bin/activate
pip3 install requirements.txt
```
to start server 
```sh
python3 server.py
```
to start client
```sh
python3 client.py
```
### How it works
Client and server communicate via tcp socket (INET/STREAM). Using grpc or xmpp was way easier option to me, but I wanted to challange myself and use something simple and to remember how to use it. 
Client GUI was created with tkinter. It was interesting option that I wanted to explore and it seemed appropriate way to do it. For using something like web based gui was better option to use with websocket or restAPI communication method.

### How I feel about this task
I spent about 3-4 hours. 
Managed implement so-so "user typing" logic. It works, but not so well. I would like to implement better one, where "typing" is not constantly streamable.
Didn't manage fully implement sent/delivered/seen. Couldn't find a way to build "seen" logic with tkinter.
Code smells. Will change that on my time.
