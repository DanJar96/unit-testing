#%%

import os, sys
import pandas as pd

currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
#%%

from order import Order, OrderStatus

#%%

def test_basic_order_default():
    """
    Does the default quantity work? 
    """
    ord = Order()
    ord.add_lineitem(111)
    ord.print_cart()
    assert ord.order_cart[111].quantity == 1
    assert ord.subtotal == 10
    ord.cancel_order()

def test_subtotal():
    """
    Testing that subtotal of order remains the same even though we 
    modify the order.
    """
    ord = Order()
    assert ord.subtotal == 0
    ord.add_lineitem(111,3)
    ord.add_lineitem(222,2)
    assert ord.subtotal == 40
    ord.modify_lineitem(111,-2)
    assert ord.order_cart[111].quantity == 1
    assert ord.subtotal == 20
    ord.cancel_order()
    assert ord.order_status == OrderStatus.CANCELLED
    
def test_order_manipulation():
    """
    What if we try and add a negative quantity of a good?
    """
    ord = Order()
    ord.add_lineitem(111,-10)
    ord.print_cart()
    assert len(ord.order_cart) == 0
    ord.add_lineitem(111,1)
    assert len(ord.order_cart) == 1
    assert ord.subtotal == 10
    ord.cancel_order()

def test_modify_nonexistent_order():
    """
    What if we try and manipulate an order that does not yet exist?
    """
    ord = Order()
    ord.modify_lineitem(111,5)
    assert len(ord.order_cart) == 0

def test_lineitem():
    """
    Testing to see that we can't try and create a lineitem for 
    more than we actually have in stock
    """
    stock = pd.read_csv("/home/dante/own_work/payment_system/database/stock.csv",
                                            sep=",",
                                            header = 0,
                                            index_col=0)
    assert stock.loc[0,'quantity_available'] > 0
    ord = Order()
    ord.add_lineitem(111,6)
    ord.print_cart()
    assert len(ord.order_cart) == 0

# %%
