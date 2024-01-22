# wARNING: this code is so sloppy and lazily written - I'll hopefully abstract stuff into helper functions and clean it up before final submission TT

# TODO 18 Jan
"""
- [ ] Trade with more than just best bid and offer for AMETHYSTS
- [ ] Split trading for each product into their own functions
- [ ] Quote AMETHYSTS
- [ ] Try to persist midmarket price for STARFRUIT
- [ ] Implement Market Making quotes and position management for other products
"""

PRICE = 0
AMOUNT = 1

MAX_POSITIONS = {
    "AMETHYSTS": 20,
    "STARFRUIT": 20,
    "ORCHIDS": 100,
    "CHOCOLATE": 250,
    "STRAWBERRIES": 350,
    "ROSES": 60,
    "GIFT_BASKET": 60,
    "COCONUT": 300,
    "COCONUT_COUPON": 600
}

NUM_CHOC_IN_GB = 4
NUM_STRAW_IN_GB = 6
NUM_ROSES_IN_GB = 1

from datamodel import ConversionObservation, OrderDepth, Symbol, TradingState, Order

class Trader:
    def run(self, state: TradingState):
        """
        Only method required. It takes all buy and sell orders for all symbols as an input,
        and outputs a list of orders to be sent
        """
        print(f"Timestamp: {state.timestamp}")
        print(f"Trader Data: {state.traderData}")
        # print(f"Observation: {state.observations}")

        result = {
            "AMETHYSTS": [],
            "STARFRUIT": [],
            "ORCHIDS": [],
            "CHOCOLATE": [],
            "STRAWBERRIES": [],
            "ROSES": [],
            "GIFT_BASKET": [],
            "COCONUT": [],
            "COCONUT_COUPON": []
        }

        # ------------------------------ AMETHYSTS -------------------------------- #
        if "AMETHYSTS" in state.order_depths.keys():
            product = "AMETHYSTS"
            orders = []
            acceptable_price = 10_000
            order_depth: OrderDepth = state.order_depths["AMETHYSTS"]
            credit = 2
            position = state.position["AMETHYSTS"]
            position_limit = MAX_POSITIONS["AMETHYSTS"]
            best_bid, best_ask = self._get_best_bid_ask(order_depth)

            if len(order_depth.sell_orders) == 0:
                orders.append(Order(product, acceptable_price + credit + 1, -position_limit))
            else:
                asks_below_price = self._get_asks_below_price(order_depth, acceptable_price + credit)
                for (price, amount) in asks_below_price:
                    print("  [AMETHYSTS] BUY", str(amount) + "x", price)
                    orders.append(Order(product, price, -amount))
                    
            if len(order_depth.buy_orders) == 0:
                orders.append(Order(product, acceptable_price - credit - 1, position_limit))
            else:
                bids_above_price = self._get_bids_above_price(order_depth, acceptable_price - credit)
                for (price, amount) in bids_above_price:
                    print("  [AMETHYSTS] SELL", str(amount) + "x", price)
                    orders.append(Order(product, price, -amount))

            result["AMETHYSTS"] = orders

        # ------------------------------ STARFRUIT -------------------------------- #
        if "STARFRUIT" in state.order_depths.keys():
            product = "STARFRUIT"
            orders = []
            acceptable_price = 5018
            credit = 7
            position = state.position["STARFRUIT"]
            position_limit = MAX_POSITIONS["STARFRUIT"]

            order_depth: OrderDepth = state.order_depths["STARFRUIT"]

            if len(order_depth.sell_orders) == 0:
                orders.append(Order(product, acceptable_price + credit + 1, -position_limit))
            else:
                asks_below_price = self._get_asks_below_price(order_depth, acceptable_price + credit)
                for (price, amount) in asks_below_price:
                    print("  [STARFRUIT] BUY", str(amount) + "x", price)
                    orders.append(Order(product, price, -amount))
            
            if len(order_depth.buy_orders) == 0:
                orders.append(Order(product, acceptable_price - credit - 1, position_limit))
            else:
                bids_above_price = self._get_bids_above_price(order_depth, acceptable_price - credit)
                for (price, amount) in bids_above_price:
                    print("  [STARFRUIT] SELL", str(amount) + "x", price)
                    orders.append(Order(product, price, -amount))

            result["STARFRUIT"] = orders

        # ---------------------------------- ORCHIDS --------------------------------- #
        if "ORCHIDS" in state.order_depths.keys():
            pass

        # ------------------------------ GIFT BASKET ARB ----------------------------- #
        # Hitting-only strategy for gift basket arbitrage
        if set(["CHOCOLATE", "STRAWBERRIES", "ROSES", "GIFT_BASKET"]).issubset(set(state.order_depths.keys())):
            # Get the best bid and ask for each product
            choc_best_bid, choc_best_ask = self._get_best_bid_ask(state.order_depths["CHOCOLATE"])
            straw_best_bid, straw_best_ask = self._get_best_bid_ask(state.order_depths["STRAWBERRIES"])
            roses_best_bid, roses_best_ask = self._get_best_bid_ask(state.order_depths["ROSES"])
            gb_best_bid, gb_best_ask = self._get_best_bid_ask(state.order_depths["GIFT_BASKET"])

            # If the cost of the gift basket is less than 6 strawberries, 4 chocolates, and 1 rose, then buy the basket and sell the individual items
            if choc_best_bid is not None and straw_best_bid is not None and roses_best_bid is not None and gb_best_ask is not None: 
                buying_price = gb_best_ask[PRICE]

                # Calculate the selling price for filling the bids
                choc_orders, remaining_choc_vol = self._get_orders_for_vol(state.order_depths["CHOCOLATE"], NUM_CHOC_IN_GB, "BIDS")
                straw_orders, remaining_straw_vol = self._get_orders_for_vol(state.order_depths["STRAWBERRIES"], NUM_STRAW_IN_GB, "BIDS")
                roses_orders, remaining_roses_vol = self._get_orders_for_vol(state.order_depths["ROSES"], NUM_ROSES_IN_GB, "BIDS")

                if remaining_choc_vol > 0 or remaining_straw_vol > 0 or remaining_roses_vol > 0:
                    print("  Not enough bids to fill gift basket")

                else: 
                    selling_price = sum([order[PRICE] * order[AMOUNT] for order in choc_orders]) + sum([order[PRICE] * order[AMOUNT] for order in straw_orders]) + sum([order[PRICE] * order[AMOUNT] for order in roses_orders])
                    if (
                        buying_price < selling_price
                        and self._get_position(state, "GIFT_BASKET") + 1 < MAX_POSITIONS["GIFT_BASKET"]
                        and self._get_position(state, "CHOCOLATE") - NUM_CHOC_IN_GB > -MAX_POSITIONS["CHOCOLATE"]
                        and self._get_position(state, "STRAWBERRIES") - NUM_STRAW_IN_GB > -MAX_POSITIONS["STRAWBERRIES"]
                        and self._get_position(state, "ROSES") - NUM_ROSES_IN_GB > -MAX_POSITIONS["ROSES"]
                    ):
                        # raise ValueError("buying_price < selling_price")
                        print("  [GB] BUY", str(gb_best_ask[AMOUNT]) + "x", gb_best_ask[PRICE])
                        print(f"  [CHOC] SELL {str(NUM_CHOC_IN_GB)}x {choc_best_bid[PRICE]}, [STRAW] SELL {str(NUM_STRAW_IN_GB)}x {straw_best_bid[PRICE]}, [ROSES] SELL {str(NUM_ROSES_IN_GB)}x {roses_best_bid[PRICE]}")
                        result["GIFT_BASKET"].append(Order("GIFT_BASKET", gb_best_ask[PRICE], gb_best_ask[AMOUNT]))
                        result["CHOCOLATE"].append(Order("CHOCOLATE", choc_best_bid[PRICE], -NUM_CHOC_IN_GB))
                        result["STRAWBERRIES"].append(Order("STRAWBERRIES", straw_best_bid[PRICE], -NUM_STRAW_IN_GB))
                        result["ROSES"].append(Order("ROSES", roses_best_bid[PRICE], -NUM_ROSES_IN_GB))
                    else:
                        print("  No profitable buy gift basket arb found")

            # If the cost of the gift basket is more than 6 strawberries, 4 chocolates, and 1 rose, then sell the basket and buy the individual items
            if choc_best_ask is not None and straw_best_ask is not None and roses_best_ask is not None and gb_best_bid is not None:
                selling_price = gb_best_bid[PRICE]

                # Calculate the buying price for filling the asks
                choc_orders, remaining_choc_vol = self._get_orders_for_vol(state.order_depths["CHOCOLATE"], NUM_CHOC_IN_GB, "ASKS")
                straw_orders, remaining_straw_vol = self._get_orders_for_vol(state.order_depths["STRAWBERRIES"], NUM_STRAW_IN_GB, "ASKS")
                roses_orders, remaining_roses_vol = self._get_orders_for_vol(state.order_depths["ROSES"], NUM_ROSES_IN_GB, "ASKS")

                if remaining_choc_vol > 0 or remaining_straw_vol > 0 or remaining_roses_vol > 0:
                    print(f"  Not enough asks to fill gift basket. Remaining choc: {remaining_choc_vol}, straw: {remaining_straw_vol}, roses: {remaining_roses_vol}")
                    
                else:
                    buying_price = sum([order[PRICE] * order[AMOUNT] for order in choc_orders]) + sum([order[PRICE] * order[AMOUNT] for order in straw_orders]) + sum([order[PRICE] * order[AMOUNT] for order in roses_orders])
                    

                    if (
                        buying_price < selling_price
                        and self._get_position(state, "GIFT_BASKET") - 1 > -MAX_POSITIONS["GIFT_BASKET"]
                        and self._get_position(state, "CHOCOLATE") + NUM_CHOC_IN_GB < MAX_POSITIONS["CHOCOLATE"]
                        and self._get_position(state, "STRAWBERRIES") + NUM_STRAW_IN_GB < MAX_POSITIONS["STRAWBERRIES"]
                        and self._get_position(state, "ROSES") + NUM_ROSES_IN_GB < MAX_POSITIONS["ROSES"]
                    ):
                        # Add orders to the result
                        print("  [GB] SELL", str(gb_best_bid[AMOUNT]) + "x", gb_best_bid[PRICE])
                        print(f"  [CHOC] BUY {str(NUM_CHOC_IN_GB)}x {choc_best_ask[PRICE]}, [STRAW] BUY {str(NUM_STRAW_IN_GB)}x {straw_best_ask[PRICE]}, [ROSES] BUY {str(NUM_ROSES_IN_GB)}x {roses_best_ask[PRICE]}")
                        result["GIFT_BASKET"].append(Order("GIFT_BASKET", gb_best_bid[PRICE], -gb_best_bid[AMOUNT]))
                        result["CHOCOLATE"].append(Order("CHOCOLATE", choc_best_ask[PRICE], NUM_CHOC_IN_GB))
                        result["STRAWBERRIES"].append(Order("STRAWBERRIES", straw_best_ask[PRICE], NUM_STRAW_IN_GB))
                        result["ROSES"].append(Order("ROSES", roses_best_ask[PRICE], NUM_ROSES_IN_GB))

                        # Remove the orders from the order depths
                        # for p in ["GIFT_BASKET", "CHOCOLATE", "STRAWBERRIES", "ROSES"]:
                        #     for order in result[p]:
                        #         del state.order_depths[p][]
                    else:
                        print("  No profitable sell gift basket arb found")


        # String value holding Trader state data required.
        # It will be delivered as TradingState.traderData on next execution.
        traderData = ""

        # Sample conversion request. Check more details below.
        conversions = 1
        return result, conversions, traderData
    
    def _get_conversion_obs_string(self, obs: ConversionObservation):
        return f"  ConversionObservation(bidPrice: {obs.bidPrice}, askPrice: {obs.askPrice}, transportFees: {obs.transportFees}, exportTariff: {obs.exportTariff}, importTariff: {obs.importTariff}, sunlight: {obs.sunlight}, humidity: {obs.humidity})"
    
    def _get_best_bid_ask(self, order_depth: OrderDepth):
        """
        Returns the largest bid and smallest ask in the order depth. 
        If there are no bids or asks, returns None
        """
        if len(order_depth.buy_orders) == 0:
            best_bid = None
        else:
            best_bid = sorted(list(order_depth.buy_orders.items()))[-1]

        if len(order_depth.sell_orders) == 0:
            best_ask = None
        else:
            best_ask = sorted(list(order_depth.sell_orders.items()))[0]
        return best_bid, best_ask

    def _get_bids_above_price(self, order_depth: OrderDepth, price: int):
        """
        Returns a list of all bids above or equal a certain price
        """
        return [bid for bid in order_depth.buy_orders.items() if bid[PRICE] >= price]
    
    def _get_asks_below_price(self, order_depth: OrderDepth, price: int):
        """
        Returns a list of all asks below or equal a certain price
        """
        return [ask for ask in order_depth.sell_orders.items() if ask[PRICE] <= price]

    def _get_position(self, state: TradingState, product: str):
        """
        Returns the position of a product
        """
        if product in state.position.keys():
            return state.position[product]
        else:
            return 0
    def _get_orders_for_vol(self, order_depth: OrderDepth, vol: int, bid_or_ask: str):
        """
        Returns a list of orders that will fill a certain volume
        """
        if bid_or_ask == "BIDS":
            orders = order_depth.buy_orders
        elif bid_or_ask == "ASKS":
            orders = order_depth.sell_orders
        else:
            raise ValueError("buy_or_sell must be either 'BIDS' or 'ASKS'")

        orders_to_fill_vol = []
        vol_remaining = vol
        for order in orders.items():
            if order[AMOUNT] >= vol_remaining:
                orders_to_fill_vol.append((order[PRICE], vol_remaining))
                vol_remaining = 0
                break
            else:
                orders_to_fill_vol.append(order)
                vol_remaining -= order[AMOUNT]
        return orders_to_fill_vol, vol_remaining
    def _print_market_data(self, state: TradingState, product: Symbol, acceptable_price: int):
        """
        Prints out useful market data for debugging
        """
        order_depth: OrderDepth = state.order_depths[product]
        position = state.position[product] if product in state.position.keys() else 0
        best_bid, best_ask = list(order_depth.buy_orders.items())[-1], list(order_depth.sell_orders.items())[0]
        midmarket = int((best_bid[0] + best_ask[0])/2)

        print(f"  Midmarket: {midmarket}")
        print(f"  Position : {position}")
        print(f"  Acceptable price : {acceptable_price}")
        print(f"  Bids: {list(order_depth.buy_orders.items())}")
        print(f"  Asks: {list(order_depth.sell_orders.items())}\n")
        print(f"  BestBid, BestAsk = {self._get_best_bid_ask(order_depth)}")
        print(f"  Market Trades: {state.market_trades[product] if product in state.market_trades.keys() else []}")
        print(f"  Own Trades: {state.own_trades[product] if product in state.own_trades.keys() else []}\n")