from brownie import  Contract
import redis
import json, time
import brownie
import threading
import yaml


class EventMonitor():


    POSITION = {
        "owner" : "",
        "creationTime" : 0,
        "lastUpdateTime" : 0,
        "collateralAmount" : 0,
        "body" : 0,
        "interest" : 0,
        "borrowFee" : 0,
        "liquidationPrice" : 0
    }

    REDIS = redis.Redis(host='localhost', port=6379, decode_responses=True)

    def _load_block_number_from_file():
        try:
            with open('monitor/monitor-config.yaml', 'r') as f:
                config = yaml.safe_load(f)
                last_recorded_block = config['monitor']['last_handled_block']
        except:
            last_recorded_block = 0
        return last_recorded_block
    
    def _get_abi_from_file(self):
        with open('ABI/Credit.json', 'r') as f:
            creditAbi = json.loads(f.read())
        return creditAbi


    def __init__(self, contract_address, last_handled_block=_load_block_number_from_file()):
        self.contract = Contract.from_abi("Credit", contract_address, self._get_abi_from_file())
        # self.contract = Contract(contract_address)
        self.last_handled_block = last_handled_block

        self.stop_event = threading.Event()
        self.listener = threading.Thread(target=self.listen)
        self.listener.start()

        self.sync_events()


    def sync_events(self):
        print("Start syncing...")
        if self.stop_event.is_set():
            self.stop_event.clear()
            self.listener = threading.Thread(target=self.listen)
            self.listener.start()       
        
        print("Syncing old events....")
        events = self.contract.events.get_sequence(
            from_block=self.last_handled_block
        )
        
        for event in events["CreatePosition"]:
            self._create_position(event)
        
        for event in events["UpdatePosition"]:
            self._update_position(event)
        
        for event in events["ClosePosition"]:
            self._close_position(event)

        print("Syncing finished...")



    def listen(self):
        print("Start listening to new events...")
        self.contract.events.subscribe(
            "CreatePosition",
            callback=self._create_position,
            delay=8,
        )
        self.contract.events.subscribe(
            "UpdatePosition",
            callback=self._update_position,
            delay=8,
        )
        self.contract.events.subscribe(
            "ClosePosition",
            callback=self._close_position,
            delay=8,
        )
        while not self.stop_event.is_set():
            time.sleep(1)

            
    def stop(self):
        print("Stopping event listener...")
        with open('monitor/monitor-config.yaml', "w") as file:
            yaml.dump({'monitor': {'last_handled_block': self.last_handled_block}}, file)
        self.stop_event.set()
        # self.listener.join()



    def _create_position(self, event):
        print(f'Create event captured {event}\n')
        args = event["args"]        
        _position = self.POSITION.copy()
        owner = args["owner"]

        _position["owner"] = owner
        _position["creationTime"] = args["timestamp"]
        _position["lastUpdateTime"] = args["timestamp"]
        _position["collateralAmount"] = args["collateralAmount"]
        _position["body"] = args["body"]
        _position["interest"] = 0
        _position["borrowFee"] = args["borrowFee"]
        _position["liquidationPrice"] = args["liquidationPrice"]

        if not self.REDIS.exists(owner):
            self.REDIS.hset(owner, mapping=_position)
            print(f'Created Position: {self.REDIS.hgetall(owner)}\n\n')
        else:
            exist_position = self.REDIS.hgetall(owner)
            if int(args["timestamp"]) > int(exist_position['lastUpdateTime']) and  int(exist_position['creationTime']) == 0:
                self.REDIS.hset(owner, mapping=_position)
                print(f'Created Position: {self.REDIS.hgetall(owner)}\n\n')
        
        if event['blockNumber'] > self.last_handled_block:
            self.last_handled_block = event['blockNumber']



    def _update_position(self, event):
        print(f'Update event captured {event}\n')
        args = event["args"]        
        owner = args["owner"]

        _position = self.REDIS.hgetall(owner).copy()

        _position["owner"] = owner
        _position["lastUpdateTime"] = args["timestamp"]
        _position["collateralAmount"] = args["newCollateralAmount"]
        _position["body"] = args["newBody"]
        _position["interest"] = args["newInterest"]
        _position["borrowFee"] = args["newBorrowFee"]
        _position["liquidationPrice"] = args["newLiquidationPrice"]

        if self.REDIS.exists(owner):
            exist_position = self.REDIS.hgetall(owner)
            if int(args["timestamp"]) > int(exist_position['lastUpdateTime']):
                self.REDIS.hset(owner, mapping=_position)
                print(f'Updated Position: {self.REDIS.hgetall(owner)}\n\n')
        else:
            print("ERROR, Position Not Found!!!\n\n")
        
        if event['blockNumber'] > self.last_handled_block:
            self.last_handled_block = event['blockNumber']

    def _close_position(self, event):
        print(f'Close event captured {event}\n')
        args = event["args"]        
        owner = args["owner"]
        _position = self.POSITION.copy()

        _position["owner"] = owner
        _position["lastUpdateTime"] = args['timestamp']

        if self.REDIS.exists(owner):
            exist_position = self.REDIS.hgetall(owner)
            if int(args["timestamp"]) > int(exist_position['lastUpdateTime']):
                print(f'Closing Position: {exist_position}\n\n')
                self.REDIS.hset(owner, mapping=_position)
        else:
            print("ERROR, Position Not Found!!!")

        if event['blockNumber'] > self.last_handled_block:
            self.last_handled_block = event['blockNumber']
