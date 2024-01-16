from datamodel import Listing, OrderDepth, Trade, TradingState
from trader import Trader

timestamp = 1000

listings = {
    "STARFRUIT": Listing(
        symbol="STARFRUIT", product="STARFRUIT", denomination="SEASHELLS"
    ),
    "AMETHYSTS": Listing(
        symbol="AMETHYSTS", product="AMETHYSTS", denomination="SEASHELLS"
    ),
}

order_depths = {
    "STARFRUIT": OrderDepth(buy_orders={10: 7, 9: 5}, sell_orders={11: -4, 12: -8}),
    "AMETHYSTS": OrderDepth(buy_orders={142: 3, 141: 5}, sell_orders={144: -5, 145: -8}),
}

own_trades = {"STARFRUIT": [], "AMETHYSTS": []}

market_trades = {
    "STARFRUIT": [
        Trade(
            symbol="STARFRUIT", price=11, quantity=4, buyer="", seller="", timestamp=900
        )
    ],
    "AMETHYSTS": [],
}

position = {"STARFRUIT": 3, "AMETHYSTS": -5}

observations = Observation()

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
