from datamodel import OrderDepth, Symbol, TradingState, Order


class Trader:
    def run(self, state: TradingState):
        """
        Only method required. It takes all buy and sell orders for all symbols as an input,
        and outputs a list of orders to be sent
        """
        print("traderData: " + state.traderData)
        print("Observations: " + str(state.observations))

        # Orders to be placed on exchange matching engine
        result: dict[Symbol, list[Order]] = {}
        for product in state.order_depths:
            order_depth: OrderDepth = state.order_depths[product]
            # Initialize the list of Orders to be sent as an empty list
            orders: list[Order] = []
            # Define a fair value for the PRODUCT. Might be different for each tradable item
            # Note that this value of 10 is just a dummy value, you should likely change it!
            acceptable_price = 10000 if (product == "AMETHYSTS") else 5040
            # All print statements output will be delivered inside test results
            print("Acceptable price : " + str(acceptable_price))
            print(
                "Buy Order depth : "
                + str(len(order_depth.buy_orders))
                + ", Sell order depth : "
                + str(len(order_depth.sell_orders))
            )

            # Order depth list come already sorted.
            # We can simply pick first item to check first item to get best bid or offer
            credit = 2
            if len(order_depth.sell_orders) != 0:
                best_ask, best_ask_amount = list(order_depth.sell_orders.items())[0]
                if int(best_ask) <= acceptable_price - credit:
                    print("BUY", str(-best_ask_amount) + "x", best_ask)
                    orders.append(Order(product, best_ask, -best_ask_amount))
            else:
                orders.append(Order(product, acceptable_price + credit, -10))
            if len(order_depth.buy_orders) != 0:
                best_bid, best_bid_amount = list(order_depth.buy_orders.items())[0]
                if int(best_bid) >= acceptable_price + credit:
                    print("SELL", str(best_bid_amount) + "x", best_bid)
                    orders.append(Order(product, best_bid, -best_bid_amount))
            else:
                orders.append(Order(product, acceptable_price - credit, 10))

            result[product] = orders

        # String value holding Trader state data required.
        # It will be delivered as TradingState.traderData on next execution.
        traderData = "SAMPLE"

        # Sample conversion request. Check more details below.
        conversions = 1
        return result, conversions, traderData
