import uuid
import datetime

from collections import deque
from bintrees import FastRBTree

# Tick inputs: action, price, qty, timestamp, side

def __main__():
    lob = LOB()
    lob.process(Tick(0,10,100,datetime.now(),0))

class LOB(object):
    def __init__(self):
        self.trades = deque(maxlen=100)
        self.bids = Tree()
        self.asks = Tree()
        self.last_tick = None
        self.last_timestamp = 0

    def process(self, tick):
        if tick.side == 0:
            tree = self.bids
        else:
            tree = self.asks

        if tick.action == 0:
            print("Inserting Order")
            tree.insert(tick)
        elif tick.action == 1:
            print("Removing Order")
            tree.remove(tick.id)
        elif tick.action == 2:
            print("Updating Order")
            tree.update(tick)
        else:
            print("Unknown Action")
        print(tree[tick.price])
        print(tree)


class Tree(object):
    def __init__(self):
        self.tree = FastRBTree()
        self.volume = 0
        self.price_map = {}
        self.order_map = {}
        self.min_price = None
        self.max_price = None

    def get_price(self, price):
        return self.price_map[price]

    def get_order(self, id):
        return self.order_map[id]

    def create_price(self, price):
        new_list = OrderList()
        self.price_tree.insert(price, new_list)
        self.price_map[price] = new_list
        if self.max_price == None or price > self.max_price:
            self.max_price = price
        if self.min_price == None or price < self.min_price:
            self.min_price = price

    def remove_price(self, price):
        self.price_tree.remove(price)
        del self.price_map[price]

        if self.max_price == price:
            try:
                self.max_price = max(self.price_tree)
            except ValueError:
                self.max_price = None
        if self.min_price == price:
            try:
                self.min_price = min(self.price_tree)
            except ValueError:
                self.min_price = None

    def price_exists(self, price):
        return price in self.price_map

    def order_exists(self, id):
        return id in self.order_map

    def insert(self, tick):
        if tick.price not in self.price_map:
            self.create_price(tick.price)
        order = Order(tick, self.price_map[tick.price])
        self.price_map[order.price].append_order(order)
        self.order_map[order.id] = order
        self.volume += order.qty

    def update(self, tick):
        order = self.order_map[tick.id]
        original_volume = order.qty
        if tick.price != order.price:
            # Price changed
            order_list = self.price_map[order.price]
            order_list.remove_order(order)
            if len(order_list) == 0:
                self.remove_price(order.price)
            self.insert_tick(tick)
            self.volume -= original_volume
        else:
            order.update_qty(tick.qty, tick.price)
            self.volume += order.qty - original_volume

    def remove(self, id):
        order = self.order_map[id]
        self.volume -= order.qty
        order.order_list.remove_order(order)
        if len(order.order_list) == 0:
            self.remove_price(order.price)
        del self.order_map[id]

    def max(self):
        return self.max_price

    def min(self):
        return self.min_price


class OrderList(object):
    def __init__(self):
        self.head_order = None
        self.tail_order = None
        self.length = 0
        self.volume = 0
        self.last = None

    def append_order(self, order):

        if len(self) == 0:
            order.next_order = None
            order.prev_order = None
            self.head_order = order
            self.tail_order = order
        else:
            order.prev_order = self.tail_order
            order.next_order = None
            self.tail_order.next_order = order
            self.tail_order = order
        self.length += 1
        self.volume += order.qty

    def remove_order(self, order):
        self.volume -= order.qty
        self.length -= 1
        if len(self) == 0:
            return
        next_order = order.next_order
        prev_order = order.prev_order
        if next_order != None and prev_order != None:
            next_order.prev_order = prev_order
            prev_order.next_order = next_order
        elif next_order != None:
            next_order.prev_order = None
            self.head_order = next_order
        elif prev_order != None:
            prev_order.next_order = None
            self.tail_order = prev_order

    def move_tail(self, order):
        if order.prev_order != None:
            order.prev_order.next_order = self.next_order
        else:
            self.head_order = order.next_order
        order.next_order.prev_order = order.prev_order
        self.tail_order.next_order = order
        self.tail_order = order
        order.prev_order = self.tail_order
        order.next_order = None


class Order(object):
    def __init__(self, tick, order_list):
        self.tick = tick
        self.order_list = order_list
        self.next_order = None
        self.prev_order = None

    def get_next_order(self):
        return self.next_order

    def get_prev_order(self):
        return self.prev_order

    def update_qty(self, new_qty, new_timestamp):
        if new_qty > self.qty and self.order_list.tail_order != self:
            self.order_list.move_tail(self)
        self.order_list.volume -= self.qty - new_qty
        self.tick.timestamp = new_timestamp
        self.tick.qty = new_qty


    def get_price(self):
        return self.tick.price

    def get_qty(self):
        return self.tick.qty

    def get_id(self):
        return self.tick.id

    def get_side(self):
        return self.tick.ask_bid


class Tick(object):
    def __init__(self, action, price, qty, timestamp, side):
        self.action = action
        self.price = price
        self.qty = qty
        self.timestamp = datetime.datetime()
        self.side = side
        self.id = uuid.uuid1()
