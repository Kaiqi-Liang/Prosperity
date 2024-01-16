from datamodel import OrderDepth, Symbol, TradingState, Order
import json

class Trader:
    def run(self, state: TradingState):
        """
        Only method required. It takes all buy and sell orders for all symbols as an input,
        and outputs a list of orders to be sent
        """
        print(f"Timestamp {state.timestamp}")
        print(f"Trader Data: {state.traderData}")
        print(f"Observations: {json.dumps(state.observations.__dict__, indent=4, sort_keys=True)}\n")

        # Orders to be placed on exchange matching engine
        result: dict[Symbol, list[Order]] = {}
        for product in state.order_depths:
            order_depth: OrderDepth = state.order_depths[product]
            # Initialize the list of Orders to be sent as an empty list
            orders: list[Order] = []

            # --------------------------------- VALUATION -------------------------------- #
            # Define a fair value for the PRODUCT. Might be different for each tradable item
            # Note that this value of 10 is just a dummy value, you should likely change it!
            if (product == "AMETHYSTS"):
                acceptable_price = 10_000
            elif (product == "ORCHIDS"):
                convObs = state.observations.conversionObservations["ORCHIDS"]
                val = 14.46 * convObs.transportFees + 5.59 * convObs.exportTariff + 8.40 * convObs.importTariff + 0.03 * convObs.sunlight+ 3.82 * convObs.humidity+ 661.70
                midmarket = (convObs.bidPrice + convObs.askPrice)/2
                acceptable_price = int(val + 0.5*midmarket)

                # Clamp the acceptable price to be between 950 to 1500
                if acceptable_price < 950:
                    acceptable_price = 950
                elif acceptable_price > 1500:
                    acceptable_price = 1500
            else:
                continue
        
            

            # Order depth list come already sorted.
            # We can simply pick first item to check first item to get best bid or offer
            if (product == "ORCHIDS"):
                credit = 5
            else:
                credit = 2
            
            if product in state.position.keys():
                position = state.position[product]
            else:
                position = 0

            # All print statements output will be delivered inside test results
            print(f"=== PRODUCT: {product} ===")
            print(f"  Position : {position}")
            print(f"  Acceptable price : {acceptable_price}\n")
            print(
                "  Buy Order depth : "
                + str(len(order_depth.buy_orders))
                + ", Sell order depth : "
                + str(len(order_depth.sell_orders))
            )

            # Position Limits
            if (product == "ORCHIDS"):
                position_limit = 100
            else:
                position_limit = 20

            if len(order_depth.sell_orders) != 0:
                best_ask, best_ask_amount = list(order_depth.sell_orders.items())[0]
                if int(best_ask) <= acceptable_price - credit and position < position_limit:
                    print("  BUY", str(-best_ask_amount) + "x", best_ask)
                    orders.append(Order(product, best_ask, -best_ask_amount))
            else:
                orders.append(Order(product, acceptable_price + credit, -10))
            if len(order_depth.buy_orders) != 0:
                best_bid, best_bid_amount = list(order_depth.buy_orders.items())[0]
                if int(best_bid) >= acceptable_price + credit and position > -position_limit:
                    print("  SELL", str(best_bid_amount) + "x", best_bid)
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
