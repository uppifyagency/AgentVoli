"""Re-run delle rotte mancate per HTTP 429 nello scan precedente.

Worker ridotti a 2 e pausa tra coppie per non triggerare il rate limit di Google.
"""

import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from agentvoli_weekend_scan import Deal, search_pair  # noqa: E402
from fli.models import Airport

MISSING_PAIRS = [
    (Airport.PSA, Airport.MUC), (Airport.PSA, Airport.AMS),
    (Airport.PSA, Airport.BER), (Airport.PSA, Airport.LHR),
    (Airport.PSA, Airport.MAD),
    (Airport.FLR, Airport.MAD), (Airport.FLR, Airport.AMS),
    (Airport.FLR, Airport.LHR), (Airport.FLR, Airport.CDG),
    (Airport.FLR, Airport.PRG), (Airport.FLR, Airport.ZRH),
    (Airport.FLR, Airport.VIE), (Airport.FLR, Airport.MUC),
    (Airport.BLQ, Airport.MAD), (Airport.BLQ, Airport.BER),
    (Airport.BLQ, Airport.LHR), (Airport.BLQ, Airport.ZRH),
    (Airport.BLQ, Airport.VIE), (Airport.BLQ, Airport.ATH),
    (Airport.BLQ, Airport.AMS), (Airport.BLQ, Airport.MUC),
]


def main():
    print("Pausa iniziale 90s per liberare il rate limit Google...")
    time.sleep(90)

    print(f"\nRe-run di {len(MISSING_PAIRS)} rotte mancanti (max_workers=2)...\n")

    all_deals: list[Deal] = []
    with ThreadPoolExecutor(max_workers=2) as ex:
        futures = {ex.submit(search_pair, o, d): (o, d) for o, d in MISSING_PAIRS}
        for fut in as_completed(futures):
            o, d = futures[fut]
            try:
                deals = fut.result()
                if deals:
                    cheapest = min(deals, key=lambda x: x.price)
                    print(f"  {o.name} -> {d.name}: {len(deals)} opzioni, min EUR {cheapest.price:.0f}")
                else:
                    print(f"  {o.name} -> {d.name}: nessuna opzione (filtri o non-stop assenti)")
                all_deals.extend(deals)
            except Exception as e:
                print(f"  [error] {o.name}->{d.name}: {e}")

    if not all_deals:
        print("\nNessuna offerta utile dalle rotte mancanti.")
        return

    all_deals.sort(key=lambda x: x.price)

    print("\n" + "=" * 80)
    print("OFFERTE DALLE ROTTE RECUPERATE (sort per prezzo)")
    print("=" * 80)
    for i, d in enumerate(all_deals[:15], 1):
        print(
            f"\n{i:2d}. {d.origin} -> {d.destination}  EUR {d.price:.0f}  "
            f"({d.out_minutes//60}h{d.out_minutes%60:02d}m / {d.ret_minutes//60}h{d.ret_minutes%60:02d}m)"
        )
        print(f"    Andata:  {d.out_dep} -> {d.out_arr}  {d.out_airline} {d.out_flight}")
        print(f"    Ritorno: {d.ret_dep} -> {d.ret_arr}  {d.ret_airline} {d.ret_flight}")


if __name__ == "__main__":
    main()
