from datamodel import Listing, OrderDepth, Trade, TradingState, Observation, ConversionObservation
from round3 import Trader

timestamp = 1000

listings = {
    "STARFRUIT": Listing(
        symbol="STARFRUIT", product="STARFRUIT", denomination="SEASHELLS"
    ),
    "AMETHYSTS": Listing(
        symbol="AMETHYSTS", product="AMETHYSTS", denomination="SEASHELLS"
    ),
    "ORCHIDS": Listing(
        symbol="ORCHIDS", product="ORCHIDS", denomination="SEASHELLS"
    ),
    "CHOCOLATE": Listing(
        symbol="CHOCOLATE", product="CHOCOLATE", denomination="SEASHELLS"
    ),
    "STRAWBERRIES": Listing(
        symbol="STRAWBERRIES", product="STRAWBERRIES", denomination="SEASHELLS"
    ),
    "ROSES": Listing(symbol="ROSES", product="ROSES", denomination="SEASHELLS"),
    "GIFT_BASKET": Listing(
        symbol="GIFT_BASKET", product="GIFT_BASKET", denomination="SEASHELLS"
    ),
}

order_depths = {
    "STARFRUIT": OrderDepth(buy_orders={10: 7, 9: 5}, sell_orders={11: -4, 12: -8}),
    "AMETHYSTS": OrderDepth(buy_orders={142: 3, 141: 5}, sell_orders={144: -5, 145: -8}),
    "ORCHIDS": OrderDepth(buy_orders={1000: 3, 999: 5}, sell_orders={1001: -5, 1002: -8}),
    "CHOCOLATE": OrderDepth(sell_orders={8017: 4}, buy_orders={8016: 4}),
    "STRAWBERRIES": OrderDepth(sell_orders={4018: 6}, buy_orders={4017: 6}),
    "ROSES": OrderDepth(sell_orders={14660: 2}, buy_orders={14659: 2}),
    "GIFT_BASKET": OrderDepth(buy_orders={71217: 1}, sell_orders={70000: 1}),
}

own_trades = {"STARFRUIT": [], "AMETHYSTS": [], "ORCHIDS": []}

market_trades = {
    "STARFRUIT": [
        Trade(
            symbol="STARFRUIT", price=11, quantity=4, buyer="", seller="", timestamp=900
        )
    ],
    "AMETHYSTS": [],
    "ORCHIDS": []
}

position = {"STARFRUIT": 3, "AMETHYSTS": -5}

observations = Observation({}, {"ORCHIDS": ConversionObservation(bidPrice= 1000, askPrice= 1000, transportFees= 0, exportTariff= 0, importTariff= 0, sunlight= 0, humidity= 0)})

state = TradingState(
    "",
    timestamp,
    listings,
    order_depths,
    own_trades,
    market_trades,
    position,
    observations,
)

trader = Trader()
print(trader.run(state))
