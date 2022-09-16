#%%
from pay.order import *
#%%

#%%
def main():
    """
    This function executes a basic order, whereby a customer
    enters into a store, adds things to their order cart, 
    and tries to pay for their order with a payment card.
    """

    a = Order()
    a.add_lineitem(111,2)
    a.add_lineitem(222,3)
    a.print_cart()
    a.cancel_order()


    return a
#%%
if __name__ == "__main__":
    main()

# %%
