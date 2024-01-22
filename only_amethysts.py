from typing import List
from datamodel import ConversionObservation, OrderDepth, Symbol, TradingState, Order
import json
from typing import Literal

# === CONSTANTS ===
PRICE = 0
VOLUME = 1

# Using variables for autocomplete
AMETHYSTS = "AMETHYSTS"
STARFRUIT = "STARFRUIT"
ORCHIDS = "ORCHIDS"
CHOCOLATE = "CHOCOLATE"
STRAWBERRIES = "STRAWBERRIES"
ROSES = "ROSES"
GIFT_BASKET = "GIFT_BASKET"
COCONUT = "COCONUT"
COCONUT_COUPON = "COCONUT_COUPON"

POSITION_LIMITS = {
    AMETHYSTS: 20,
    STARFRUIT: 20,
    ORCHIDS: 100,
    CHOCOLATE: 250,
    STRAWBERRIES: 350,
    ROSES: 60,
    GIFT_BASKET: 60,
    COCONUT: 300,
    COCONUT_COUPON: 600
}

NUM_CHOC_IN_GB = 4
NUM_STRAW_IN_GB = 6
NUM_ROSES_IN_GB = 1

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
            amethystOrders, newTraderDataObj = amethysts(state.order_depths[AMETHYSTS], state.position[AMETHYSTS], traderDataObj, state)

            result[AMETHYSTS] = amethystOrders
        
        if ORCHIDS in state.order_depths:
            pass

        if set([CHOCOLATE, STRAWBERRIES, ROSES, GIFT_BASKET]).issubset(set(state.order_depths.keys())):
            pass

        conversions = None
        
        print(f"RESULT: {result}")
        
        return result, conversions, json.dumps(traderDataObj)

def amethysts(orderDepth, position, traderDataObj, state: TradingState):
    orders: List[Order] = []

    acceptablePrice = 10_000
    credit = 2
    passiveBuffer = 1

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
    bestBid, bestAsk = get_best_bid_ask(orderDepth)
    if (bestBid == None or bestBid[PRICE] < buyQuotePrice) and position < buyPositionLimit:
        orders.append(create_order(AMETHYSTS, "BUY", buyQuotePrice, 5, isQuote=True))
    if bestAsk == None or bestAsk[PRICE] > sellQuotePrice and position :
        orders.append(create_order(AMETHYSTS, "SELL", sellQuotePrice, -5, isQuote=True))
    
    # --- HITTING ---
    # Prices I'm willing to hit
    buyHitPrice = acceptablePrice - credit
    sellHitPrice = acceptablePrice + credit
    
    # Hit all bids above sellHitPrice
    bidsToHit: List[tuple[int, int]] = get_bids_above_price(orderDepth, sellHitPrice)
    for (bidPrice, bidQuantity) in bidsToHit:
        orders.append(create_order(AMETHYSTS, "SELL", bidPrice, -bidQuantity))
        orderDepth.buy_orders.pop(bidPrice)
    
    # Lift asks below buyHitPrice
    asksToLift = get_asks_below_price(orderDepth, buyHitPrice)
    for (askPrice, askQuantity) in asksToLift:
        orders.append(create_order(AMETHYSTS, "BUY", askPrice, -askQuantity)) # negative because quantity is counterparty's quantity
        orderDepth.sell_orders.pop(askPrice)
    
    # Quote if book is empty/favourable after hitting
    bestBid, bestAsk = get_best_bid_ask(orderDepth)
    if bestBid == None or bestBid[PRICE] < buyQuotePrice:
        orders.append(create_order(AMETHYSTS, "BUY", buyQuotePrice, 5, isQuote=True))
    if bestAsk == None or bestAsk[PRICE] > sellQuotePrice:
        orders.append(create_order(AMETHYSTS, "SELL", sellQuotePrice, -5, isQuote=True))
    
    print_product_info(AMETHYSTS, orderDepth, position, buyPositionLimit, credit, passiveBuffer, acceptablePrice, orders, state)
    
    return orders, traderDataObj

def orchids(orderDepth, position, traderDataObj, conversionObservation: ConversionObservation, state: TradingState):
    orders: List[Order] = []
    conversions = 0

    convBidPrice = conversionObservation.bidPrice
    exportTariff = conversionObservation.exportTariff

    convAskPrice = conversionObservation.askPrice
    importTariff = conversionObservation.importTariff

    transportFees = conversionObservation.transportFees

    bestBid, bestAsk = get_best_bid_ask(orderDepth)

    if not bestBid or not bestAsk:
        raise ValueError("  No best bid or ask for ORCHIDS") # TODO remove for actual
        return [], 0

    positionLimit = 50

    # Check if shorting ORCHIDS is profitable (sell at bestBid and buy at convAskPrice, pay transportFees and importTariff)
    shortProfit = (bestBid[PRICE] - convAskPrice - transportFees - importTariff)*min(bestBid[VOLUME], position - positionLimit) if bestBid else 0

    # Check if longing ORCHIDS is profitable (buy at bestAsk and sell at convBidPrice, pay transportFees and exportTariff)
    longProfit = (convBidPrice - bestAsk[PRICE] - transportFees - exportTariff)*min(abs(bestAsk[VOLUME]), positionLimit - position) if bestAsk else 0

    print(f"  Short profit: {shortProfit}. ({bestBid[PRICE] - convAskPrice - transportFees - importTariff} * {min(bestBid[VOLUME], position - positionLimit)})")
    print(f"  Long profit: {longProfit}")
    print("")
    
    shortProfit = max(shortProfit, 0)
    longProfit = max(longProfit, 0)

    # We can only either go long or short, not both
    if shortProfit > longProfit:
        # Short
        if bestBid and  position > -positionLimit:
            volume = min(bestBid[VOLUME], position - positionLimit)
            orders.append(create_order(ORCHIDS, "SELL", bestBid[PRICE], -volume))

            conversions = abs(bestBid[VOLUME])
    else:
        # Long
        if bestAsk and position < positionLimit:
            volume = min(abs(bestAsk[VOLUME]), positionLimit - position)
            orders.append(create_order(ORCHIDS, "BUY", bestAsk[VOLUME], volume))

            conversions = abs(bestAsk[VOLUME])

    print_product_info(ORCHIDS, orderDepth, position, POSITION_LIMITS[ORCHIDS], 0, 0, 0, orders, state)
    print(f"  Conversions: {conversions}")
    
    return orders, conversions



def gift_basket(traderDataObj, state: TradingState):
    # TODO - currently doing single-sided arb (long gb, short components), need to do double-sided arb with max volume
    NUM_CHOC_IN_GB = 4
    NUM_STRAW_IN_GB = 6
    NUM_ROSES_IN_GB = 1

    result = {
        CHOCOLATE: [],
        STRAWBERRIES: [],
        ROSES: [],
        GIFT_BASKET: []
    }

    chocOrderDepth = state.order_depths[CHOCOLATE]
    strawOrderDepth = state.order_depths[STRAWBERRIES]
    rosesOrderDepth = state.order_depths[ROSES]
    gbOrderDepth = state.order_depths[GIFT_BASKET]

    chocBestBid, chocBestAsk = get_best_bid_ask(chocOrderDepth)
    strawBestBid, strawBestAsk = get_best_bid_ask(strawOrderDepth)
    rosesBestBid, rosesBestAsk = get_best_bid_ask(rosesOrderDepth)
    gbBestBid, gbBestAsk = get_best_bid_ask(gbOrderDepth)

    # If the cost of the gift basket is less than 6 strawberries, 4 chocolates, and 1 rose, then buy the basket and sell the individual items
    if chocBestBid is not None and strawBestBid is not None and rosesBestBid is not None and gbBestAsk is not None:
        buyPrice = gbBestAsk[PRICE]
        
        # Calculate the selling price for filling the bid volumes
        chocOrders, remainingChocVol = getOrdersForVol(chocOrderDepth, NUM_CHOC_IN_GB, "BIDS")
        strawOrders, remainingStrawVol = getOrdersForVol(strawOrderDepth, NUM_STRAW_IN_GB, "BIDS")
        rosesOrders, remainingRosesVol = getOrdersForVol(rosesOrderDepth, NUM_ROSES_IN_GB, "BIDS")
        
        if remainingChocVol > 0 or remainingStrawVol > 0 or remainingRosesVol > 0:
            print("  [Can't do long gb arb] Not enough bids to fill gift basket")

        else:
            sellingPrice = sum([order[PRICE]*abs(order[VOLUME]) for order in chocOrders]) + sum([order[PRICE]*abs(order[VOLUME]) for order in strawOrders]) + sum([order[PRICE]*abs(order[VOLUME]) for order in rosesOrders])
            profit = sellingPrice - buyPrice
            if (
                profit > 0
                and get_position(state, GIFT_BASKET) + 1 < POSITION_LIMITS[GIFT_BASKET]
                and get_position(state, CHOCOLATE) - NUM_CHOC_IN_GB > -POSITION_LIMITS[CHOCOLATE]
                and get_position(state, STRAWBERRIES) - NUM_STRAW_IN_GB > -POSITION_LIMITS[STRAWBERRIES]
                and get_position(state, ROSES) - NUM_ROSES_IN_GB > -POSITION_LIMITS[ROSES]
            ):
                result[CHOCOLATE] = [create_order(CHOCOLATE, "SELL", chocOrders[0][PRICE], -NUM_CHOC_IN_GB)]
                result[STRAWBERRIES] = [create_order(STRAWBERRIES, "SELL", strawOrders[0][PRICE], -NUM_STRAW_IN_GB)]
                result[ROSES] = [create_order(ROSES, "SELL", rosesOrders[0][PRICE], -NUM_ROSES_IN_GB)]
                result[GIFT_BASKET] = [create_order(GIFT_BASKET, "BUY", buyPrice, 1)]
                print("  [Long gb arb] Buy gift basket and sell individual items")
                print(f"    Buy price: {buyPrice}")
                print(f"    Selling price: {sellingPrice}")
                print(f"    Profit: {profit}")
                print(f"    Orders: {result}")
                return result


    return result

def print_product_info(product: Symbol, order_depth: OrderDepth, position: int, position_limit: int, credit, passiveBuffer, acceptablePrice, orders, state: TradingState):
    print(f"=== {product} ===")
    print(f"  Position: {position}/{position_limit}")
    print(f"  Bids: {sorted(order_depth.buy_orders.items(), reverse=True)}")
    print(f"  Asks: {sorted(order_depth.sell_orders.items())}")
    bestBid, bestAsk = get_best_bid_ask(order_depth)
    if bestBid and bestAsk:
        print(f"  Midmarket: {(bestBid[PRICE] + bestAsk[PRICE]) / 2}")
    print(f"  Market Trades: {state.market_trades[product]}")
    print(f"  Own Trades: {state.own_trades[product]}")
    print("")
    print(f"  Acceptable price: {acceptablePrice}")
    if credit: print(f"  Credit: {credit}")
    if passiveBuffer: print(f"  Passive buffer: {passiveBuffer}")
    print("")
    print(f"  Orders: {orders}")

def get_volume(side: str, positionLimit, position, maxVolume):
    if side not in ["BUY", "SELL"]:
        raise ValueError(f"  `side` must be either 'BUY' or 'SELL'. Received side {side}")
    if side == "BUY":
        return min(positionLimit - position, maxVolume)
    return min(-positionLimit - position, maxVolume)

def get_best_bid_ask(order_depth: OrderDepth):
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

def get_bids_above_price(order_depth: OrderDepth, price: int) -> List[tuple[int, int]]:
    """
    Returns a list of all bids above or equal a certain price
    """
    return [bid for bid in sorted(order_depth.buy_orders.items(), reverse=True) if bid[PRICE] >= price]
    
def get_asks_below_price(order_depth: OrderDepth, price: int):
    """
    Returns a list of all asks below or equal a certain price
    """
    return [ask for ask in sorted(order_depth.sell_orders.items()) if ask[PRICE] <= price]

def get_position(state: TradingState, product: Symbol):
    """
    Returns the position of a product
    """
    if product in state.position.keys():
        return state.position[product]
    else:
        return 0
    
def create_order(product: Symbol, side: str, price: int, quantity: int, isQuote: bool=False):
    if side not in ["BUY", "SELL"]:
        raise ValueError(f"  `side` must be either 'BUY' or 'SELL'. Received side {side}")
    if side == "BUY" and quantity < 0:
        raise ValueError(f"[_create_order({product}, {side}, {price}, {quantity})] BUY must have a positive quantity. Received quantity {quantity}.")
    if side == "SELL" and quantity > 0:
        raise ValueError(f"[_create_order({product}, {side}, {price}, {quantity})] BUY must have a negative quantity. Received quantity {quantity}.")
    print(f"[{product}] {'(Q)' if isQuote else ''} {side} {quantity} x ${price}")
    return Order(product, price, quantity)

def getOrdersForVol(order_depth: OrderDepth, vol: int, bid_or_ask: str):
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
            if abs(order[VOLUME]) >= vol_remaining:
                orders_to_fill_vol.append((order[PRICE], vol_remaining))
                vol_remaining = 0
                break
            else:
                orders_to_fill_vol.append(order)
                vol_remaining -= abs(order[VOLUME])
        return orders_to_fill_vol, vol_remaining