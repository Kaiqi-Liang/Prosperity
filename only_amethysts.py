from typing import List
from datamodel import ConversionObservation, OrderDepth, Symbol, TradingState, Order
import json
from typing import Literal

# === CONSTANTS ===
PRICE = 0
AMOUNT = 1

# Using variables for autocomplete
AMETHYSTS = "AMETHYSTS"

POSITION_LIMITS = {
    AMETHYSTS: 20
}

class Trader:
    def run(self, state: TradingState):
        result: dict[Symbol, list[Order]] = {}
        for product in state.order_depths:
            result[product] = []
        
        print(f"traderData: {state.traderData}")
        
        if state.traderData == "":
            traderDataObj = {}
        else:
            traderDataObj = json.loads(state.traderData)
        
        if AMETHYSTS in state.order_depths:
            orderDepth = state.order_depths[AMETHYSTS]
            acceptablePrice = 10_000
            credit = 2
            passiveBuffer = 1
            position = self._get_position(state, AMETHYSTS)
            buyPositionLimit = POSITION_LIMITS[AMETHYSTS]
            sellPositionLimit = -POSITION_LIMITS[AMETHYSTS]
            if AMETHYSTS not in traderDataObj:
                traderDataObj[AMETHYSTS] = {}
                traderDataObj[AMETHYSTS]["trades"] = []
                
            # --- QUOTING ---
            # Prices I'm willing to quote
            buyQuotePrice = acceptablePrice - credit - passiveBuffer
            sellQuotePrice = acceptablePrice + credit + passiveBuffer
            
            # Quote if the book is empty
            bestBid, bestAsk = self._get_best_bid_ask(orderDepth)
            if (bestBid == None or bestBid[PRICE] < buyQuotePrice) and position > buyPositionLimit:
                result[AMETHYSTS].append(self._create_order(AMETHYSTS, "BUY", buyQuotePrice, 5, isQuote=True))
            if bestAsk == None or bestAsk[PRICE] > sellQuotePrice:
                result[AMETHYSTS].append(self._create_order(AMETHYSTS, "SELL", sellQuotePrice, -5, isQuote=True))
            
            # --- HITTING ---
            # Prices I'm willing to hit
            buyHitPrice = acceptablePrice - credit
            sellHitPrice = acceptablePrice + credit
            
            # Hit all bids above sellHitPrice
            bidsToHit: List[tuple[int, int]] = self._get_bids_above_price(orderDepth, sellHitPrice)
            for (bidPrice, bidQuantity) in bidsToHit:
                result[AMETHYSTS].append(self._create_order(AMETHYSTS, "SELL", bidPrice, -bidQuantity))
                orderDepth.buy_orders.pop(bidPrice)
            
            # Lift asks below buyHitPrice
            asksToLift = self._get_asks_below_price(orderDepth, buyHitPrice)
            for (askPrice, askQuantity) in asksToLift:
                result[AMETHYSTS].append(self._create_order(AMETHYSTS, "BUY", askPrice, -askQuantity)) # negative because quantity is counterparty's quantity
                orderDepth.sell_orders.pop(askPrice)
            
            # Quote if book is empty/favourable after hitting
            bestBid, bestAsk = self._get_best_bid_ask(orderDepth)
            if bestBid == None or bestBid[PRICE] < buyQuotePrice:
                result[AMETHYSTS].append(self._create_order(AMETHYSTS, "BUY", buyQuotePrice, 5, isQuote=True))
            if bestAsk == None or bestAsk[PRICE] > sellQuotePrice:
                result[AMETHYSTS].append(self._create_order(AMETHYSTS, "SELL", sellQuotePrice, -5, isQuote=True))
        
        conversions = None
        
        print(f"RESULT: {result}")
        
        return result, conversions, json.dumps(traderDataObj)
    # def _valid_position(self, position: int,  side: str, positionLimit: int):
    #     """Check if our position is valid for a trade on this side

    #     Args:
    #         position (int): _description_
    #         side (str): _description_
    #         positionLimit (int): _description_
    #     """
    #     self._check_side(side)
    #     if side == "BUY" and 
    def _get_best_bid_ask(self, order_depth: OrderDepth):
        """
        Returns the largest bid and smallest ask in the order depth. 
        If there are no bids or asks, returns None
        """
        if len(order_depth.buy_orders) == 0:
            best_bid = None
        else:
            best_bid = sorted(list(order_depth.buy_orders.items()), reverse=True)[0]

        if len(order_depth.sell_orders) == 0:
            best_ask = None
        else:
            best_ask = sorted(list(order_depth.sell_orders.items()))[0]
        return best_bid, best_ask

    def _get_bids_above_price(self, order_depth: OrderDepth, price: int) -> List[tuple[int, int]]:
        """
        Returns a list of all bids above or equal a certain price
        """
        return [bid for bid in sorted(order_depth.buy_orders.items(), reverse=True) if bid[PRICE] >= price]
    
    def _get_asks_below_price(self, order_depth: OrderDepth, price: int):
        """
        Returns a list of all asks below or equal a certain price
        """
        return [ask for ask in sorted(order_depth.sell_orders.items()) if ask[PRICE] <= price]

    def _get_position(self, state: TradingState, product: Symbol):
        """
        Returns the position of a product
        """
        if product in state.position.keys():
            return state.position[product]
        else:
            return 0
    
    def _create_order(self, product: Symbol, side: str, price: int, quantity: int, isQuote: bool=False):
        if side not in ["BUY", "SELL"]:
            raise ValueError(f"  `side` must be either 'BUY' or 'SELL'. Received side {side}")
        if side == "BUY" and quantity < 0:
            raise ValueError(f"[_create_order({product}, {side}, {price}, {quantity})] BUY must have a positive quantity. Received quantity {quantity}.")
        if side == "SELL" and quantity > 0:
            raise ValueError(f"[_create_order({product}, {side}, {price}, {quantity})] BUY must have a negative quantity. Received quantity {quantity}.")
        print(f"[{product}] {'(Q)' if isQuote else ''} {side} {quantity} x ${price}")
        return Order(product, price, quantity)