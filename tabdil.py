from tabdeal.spot import Spot
from tabdeal.enums import OrderSides, OrderTypes

client = Spot(api_key, api_secret)

order = client.new_order(
    symbol='BTCIRT',
    side=OrderSides.SELL,
    type=OrderTypes.MARKET,
    quantity="0.001"
)

