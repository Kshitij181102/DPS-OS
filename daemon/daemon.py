#!/usr/bin/env python3
# daemon/daemon.py
import argparse, socket, json, threading, time, sqlite3, os
from ruleEngine import RuleEngine
from actionDispatcher import ActionDispatcher

SOCK_PATH = '/var/run/dpsos.sock'

class DPSDaemon:
    def __init__(self, dbPath):
        self.ruleEngine = RuleEngine(dbPath)
        self.actionDispatcher = ActionDispatcher()
        if os.path.exists(SOCK_PATH):
            os.remove(SOCK_PATH)
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.bind(SOCK_PATH)
        os.chmod(SOCK_PATH, 0o660)
        self.sock.listen(5)

    def serve_forever(self):
        print('DPSDaemon listening on', SOCK_PATH)
        while True:
            conn, _ = self.sock.accept()
            threading.Thread(target=self.handle_conn, args=(conn,)).start()

    def handle_conn(self, conn):
        try:
            data = conn.recv(8192).decode()
            evt = json.loads(data)
            print('Event:', evt)
            edge = self.ruleEngine.evaluate(evt)
            if edge:
                print('Transition:', edge)
                self.actionDispatcher.applyActions(edge.get('actions', []))
        except Exception as e:
            print('Error handling conn', e)
        finally:
            conn.close()

if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--db','-d', default='daemon/config.sqlite')
    args = parser.parse_args()
    d = DPSDaemon(args.db)
    d.serve_forever()