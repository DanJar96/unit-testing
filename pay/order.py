#%%

import enum
import os
import pandas as pd
from enum import Enum


#%%
def order_num():
    """
    This function will assign an order to the latest order number
    in the store. In other words, it will cross-reference to a data-base
    to see what the next order number should be. This is good so that we 
    can 'automatically' track how many orders have come through the system 
    in total. It also makes sure that we don't have duplicate order numbers. 
    """
    # start by retreiving latest order, and appending a new order
    with open("database/order_history.txt", 'r') as order_history:
        order_list = order_history.readlines()
        orders_sum = len(order_list)
        # print(orders_sum)

    with open("database/order_history.txt", 'a') as order_history:
        order_history.write(str(orders_sum+1)+"\n")
    return orders_sum+1

def reserve_in_stock(id : int, quantity : int):
    """
    Reserves quantity of id from stock
    Parameters
    ----------
    id : item id of good to be released
    quantity : quantity of good to be reserved
    Returns
    -------
    reserve_flag : was the reservation successful?
    """
    stock = pd.read_csv("database/stock.csv",
                                                        sep = ",",
                                                        header = 0,
                                                        index_col = 0)
    index_position_of_item = stock.index[stock.item_id == id].to_list()[0] 
    available = stock.at[index_position_of_item,'quantity_available']

    # if we don't have enough item in stock, make unusuccessful attempt
    # print(f"Wanted {quantity} number of id {id}...")
    # print(f"Found {available} number of id {id} in stock...")
    if available < quantity:
        reserve_flag = False
    else: 
        reserve_flag = True
        stock.at[index_position_of_item,'quantity_reserved'] += quantity
        stock.at[index_position_of_item,'quantity_available'] -= quantity
        stock.to_csv("database/stock.csv",
                                            sep = ",")

    
    return reserve_flag


def release_in_stock(id : int, quantity : int):
    """
    Releases quantity of id from reserved in stock
    Parameters
    ----------
    id : item id of good to be released
    quantity : quantity of good to be released
    Returns
    -------
    release_flag : was the release successful?
    """
    stock = pd.read_csv("database/stock.csv",
                                                sep = ",",
                                                header = 0,
                                                index_col = 0)
    index_position_of_item = stock.index[stock.item_id == id].to_list()[0]
    stock.at[index_position_of_item,'quantity_available'] += quantity
    stock.at[index_position_of_item,'quantity_reserved'] -= quantity
    stock.to_csv("database/stock.csv",
                                            sep = ",")
    release_flag = True

    return release_flag

def exists_in_stock(id : int):
    """
    Checks if item id exists in stock
    Parameters
    ----------
    id : item id to be checked if exists
    Returns
    -------
    exists_flag : does the id exist in our stock?
    """
    stock_available_ids = pd.read_csv("database/stock.csv",
                                            sep=",",
                                            header = 0,
                                            index_col=0).iloc[:,0].astype(int).to_list()

    if id not in stock_available_ids:
        exists_flag = False
    else:
        exists_flag = True
    
    return exists_flag

def getprice(id : int):
    """
    Retreives the price of an item based on id 
    from the database
    Parameters
    ----------
    id : item id to be priced
    Returns
    -------
    price : unit price of the item
    """
    stock = pd.read_csv("database/stock.csv",
                                                sep = ",",
                                                header = 0,
                                                index_col = 0)
    position = stock.index[stock.item_id == id].to_list()
    if len(position) == 0:
        price = 0
    else:
        index_position_of_item = position[0]
        rawprice = stock.at[index_position_of_item,'price']
        price = float(str(rawprice).replace("_",'.')) 
    return price

    
class OrderStatus(Enum):
    PENDING = 'pending'
    PAID = 'paid'
    CANCELLED = 'cancelled'

class LineItemStatus(Enum):
    ADDED = 'successfully added to cart'
    NOT_ADDED = 'did not add to cart'


class lineitem:
    def __init__(self,id : int,quantity : int = 1):
        """
        Initializes the lineitem class. 
        If exists, will attempt to reserve in stock.
        Parameters
        ----------
        id : item id of good to be reserved
        quantity : quantity of good to be reserved
        """
        if reserve_in_stock(id = id, quantity = quantity):
            self.quantity = quantity
            self.id = id
            self.price = getprice(id) * quantity
            self.successflag = LineItemStatus.ADDED
        else:
            self.successflag = LineItemStatus.NOT_ADDED
 
#%%
class Order:
    order_cart : list[lineitem] = []
    order_status : OrderStatus = OrderStatus.PENDING
    def __init__(self):
        """
        Initializes the order class.
        Assigns a unique order number to the order.
        """
        self.__order_num = order_num()
        self.order_cart = {}

    @property
    def order_num(self):
        """
        Defining the order number as immutable.
        This could be changed later if we want to be able to
        merge two orders into one (idk why).
        """
        return self.__order_num
    
    @property
    def subtotal(self):
        """
        Defining the subtotal of the whole cart as a 
        property of the class.
        """
        if len(self.order_cart) == 0:
            return 0
        else:
            return sum([v.quantity*getprice(k) for k,v in self.order_cart.items()])
    
    def add_lineitem(self,id : int = 1, quantity: int = 1):
        """
        Attempts to add quantity of item id to the order cart as a lineitem.
        Notice that this happens through the lineitem class.
        Parameters
        ----------
        id : item id of good to be added
        quantity : quantity of good to be added
        Comments
        --------
        Would be better to have another function that checks existance & stock
        instead of just checking if it exists. Then the second if statement 
        would not be needed.
        """
        if quantity > 0 and exists_in_stock(id):
            self.order_cart[id] = lineitem(id = id, quantity = quantity)
            if self.order_cart[id].successflag == LineItemStatus.NOT_ADDED:
                self.order_cart.pop(id)


    def modify_lineitem(self, id : int = 1, quantity : int = 1):
        """
        Attempts to modify an existing line item by either adding or subtracting
        quantity from existing lineitem with item id, and if goes below zero 
        then actually deletes the lineitem from the order cart completely
        Parameters
        ----------
        id : item id of good to be modified
        quantity : quantity of good to be modified (either added or subtracted)

        """
        # if the line item becomes quantity zero or less, then get rid of it.
        if self.order_cart.get(id) != None:
            if self.order_cart[id].quantity + quantity < 1:
                release_in_stock(id = id, quantity = self.order_cart[id].quantity)
                self.order_cart.pop(id)
            # elif the line item quantity does not become zero or less, then we will 
            # just decrement or increment it by how much it is
            elif quantity >= 0:
                if reserve_in_stock(id = id, quantity = quantity):
                    self.order_cart[id].quantity += quantity
            # if the line item quantity is decreased, but not zero.
            elif quantity < 0:
                release_in_stock(id = id, quantity = -1 * quantity)
                self.order_cart[id].quantity += quantity

    def print_cart(self):
        """
        Prints out the content of the order cart in the current session
        """
        print([(self.order_num,k,v.quantity,getprice(k)*v.quantity) if not isinstance(v, int) 
                                            else (self.order_num, k, v, 0) 
                                            for k,v in self.order_cart.items()])

    def cancel_order(self):
        """
        Releases all items (and their quantites) that are currently 
        reserved in the order cart.
        """
        self.cart_copy = self.order_cart.copy()
        for k,v in self.cart_copy.items():
            self.modify_lineitem(id = k, quantity = -1 * v.quantity)
        self.order_status  = OrderStatus.CANCELLED

# %%
