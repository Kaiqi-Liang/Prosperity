from datamodel import Listing, OrderDepth, Trade, TradingState, Observation, ConversionObservation
from only_amethysts import Trader

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
    # "STARFRUIT": OrderDepth(buy_orders={10: 7, 9: 5}, sell_orders={11: -4, 12: -8}),
    "AMETHYSTS": OrderDepth(buy_orders={142: 3, 141: 5}, sell_orders={144: -5, 145: -8}),
    # "ORCHIDS": OrderDepth(buy_orders={1000: 3, 999: 5}, sell_orders={1001: -5, 1002: -8}),
    "CHOCOLATE": OrderDepth( buy_orders={7750: 136}, sell_orders={7752: 136}),
    "GIFT_BASKET": OrderDepth(buy_orders={69548: 2}, sell_orders={69559: 1}),
    "ROSES": OrderDepth(buy_orders={14415:53}, sell_orders={14416: 53}),
    "STRAWBERRIES": OrderDepth(buy_orders={3984: 272}, sell_orders={3986: 272}),
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
