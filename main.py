import aiohttp
import asyncio
import argparse
from datetime import datetime, timedelta
from collections import defaultdict

class ExchangeRateFetcher:
    API_URL = "https://api.privatbank.ua/p24api/exchange_rates?json&date="

    async def fetch_exchange_rate(self, date):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.API_URL + date) as response:
                data = await response.json()
                return data['exchangeRate']

    async def fetch_rates_for_last_n_days(self, n):
        today = datetime.today()
        dates = [(today - timedelta(days=i)).strftime('%d.%m.%Y') for i in range(n)]
        tasks = [self.fetch_exchange_rate(date) for date in dates]
        return await asyncio.gather(*tasks)

def parse_args():
    parser = argparse.ArgumentParser(description='Fetch exchange rates from PrivatBank API.')
    parser.add_argument('days', type=int, help='Number of days to retrieve exchange rates (up to 10 days)')
    return parser.parse_args()

async def main():
    args = parse_args()
    if args.days > 10:
        print("Error: Cannot retrieve rates for more than 10 days.")
        return

    fetcher = ExchangeRateFetcher()
    rates_list = await fetcher.fetch_rates_for_last_n_days(args.days)

    result = defaultdict(dict)
    for date, rates in zip([(datetime.today() - timedelta(days=i)).strftime('%d.%m.%Y') for i in range(args.days)], rates_list):
        for r in rates:
            currency = r["currency"]
            result[date][currency] = {'sale': r['saleRateNB'], 'purchase': r['purchaseRateNB']} 
    final_result = [{date: currencies} for date, currencies in result.items()]

    print(final_result)

if __name__ == "__main__":
    asyncio.run(main())
