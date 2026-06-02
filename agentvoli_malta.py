"""AgentVoli — cerca voli Roma (FCO) -> Malta (MLA), andata e ritorno.

Andata:  oggi o domani (calcolati a runtime)
Ritorno: da 1 a 6 giorni dopo l'andata
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import date, timedelta

from fli.models import (
    Airport,
    FlightSearchFilters,
    FlightSegment,
    MaxStops,
    PassengerInfo,
    SeatType,
    SortBy,
    TripType,
)
from fli.search import SearchFlights

ORIGIN = Airport.FCO
DEST = Airport.MLA
_TODAY = date.today()
OUTBOUND_DATES = [_TODAY.isoformat(), (_TODAY + timedelta(days=1)).isoformat()]
RETURN_OFFSETS = [1, 2, 3, 4, 5, 6]  # giorni dopo l'andata


@dataclass
class Deal:
    out_date: str
    ret_date: str
    price: float
    out_dep: str
    out_arr: str
    out_airline: str
    out_flight: str
    out_minutes: int
    out_stops: int
    ret_dep: str
    ret_arr: str
    ret_airline: str
    ret_flight: str
    ret_minutes: int
    ret_stops: int


def search_pair(out_date: str, ret_date: str) -> list[Deal]:
    filters = FlightSearchFilters(
        trip_type=TripType.ROUND_TRIP,
        passenger_info=PassengerInfo(adults=1),
        seat_type=SeatType.ECONOMY,
        stops=MaxStops.ANY,
        sort_by=SortBy.CHEAPEST,
        flight_segments=[
            FlightSegment(
                departure_airport=[[ORIGIN, 0]],
                arrival_airport=[[DEST, 0]],
                travel_date=out_date,
            ),
            FlightSegment(
                departure_airport=[[DEST, 0]],
                arrival_airport=[[ORIGIN, 0]],
                travel_date=ret_date,
            ),
        ],
    )

    deals: list[Deal] = []
    try:
        results = SearchFlights().search(filters) or []
    except Exception as e:
        print(f"  [skip] {out_date} -> {ret_date}: {type(e).__name__}: {e}")
        return deals

    for outbound, ret in results:
        ol_first, ol_last = outbound.legs[0], outbound.legs[-1]
        rl_first, rl_last = ret.legs[0], ret.legs[-1]
        deals.append(Deal(
            out_date=out_date,
            ret_date=ret_date,
            price=float(outbound.price),
            out_dep=ol_first.departure_datetime.strftime("%a %d-%b %H:%M"),
            out_arr=ol_last.arrival_datetime.strftime("%H:%M"),
            out_airline=ol_first.airline.name,
            out_flight=str(ol_first.flight_number),
            out_minutes=outbound.duration,
            out_stops=outbound.stops,
            ret_dep=rl_first.departure_datetime.strftime("%a %d-%b %H:%M"),
            ret_arr=rl_last.arrival_datetime.strftime("%H:%M"),
            ret_airline=rl_first.airline.name,
            ret_flight=str(rl_first.flight_number),
            ret_minutes=ret.duration,
            ret_stops=ret.stops,
        ))
    return deals


def main():
    pairs = []
    for out_date in OUTBOUND_DATES:
        d = date.fromisoformat(out_date)
        for off in RETURN_OFFSETS:
            pairs.append((out_date, (d + timedelta(days=off)).isoformat()))

    print(f"Scansione {len(pairs)} combinazioni FCO <-> MLA (andata e ritorno)...\n")

    all_deals: list[Deal] = []
    with ThreadPoolExecutor(max_workers=8) as ex:
        futures = {ex.submit(search_pair, o, r): (o, r) for o, r in pairs}
        for fut in as_completed(futures):
            o, r = futures[fut]
            try:
                deals = fut.result()
                if deals:
                    cheapest = min(deals, key=lambda x: x.price)
                    print(f"  {o} -> {r}: {len(deals)} opzioni, min EUR {cheapest.price:.0f}")
                else:
                    print(f"  {o} -> {r}: nessuna opzione")
                all_deals.extend(deals)
            except Exception as e:
                print(f"  [error] {o}->{r}: {e}")

    if not all_deals:
        print("\nNessuna offerta trovata.")
        return

    all_deals.sort(key=lambda x: x.price)

    print("\n" + "=" * 80)
    print("TOP 12 OFFERTE  ROMA (FCO) <-> MALTA (MLA)")
    print("=" * 80)
    for i, d in enumerate(all_deals[:12], 1):
        oh = f"{d.out_minutes // 60}h{d.out_minutes % 60:02d}m"
        rh = f"{d.ret_minutes // 60}h{d.ret_minutes % 60:02d}m"
        ostop = "diretto" if d.out_stops == 0 else f"{d.out_stops} scalo/i"
        rstop = "diretto" if d.ret_stops == 0 else f"{d.ret_stops} scalo/i"
        print(f"\n{i:2d}. EUR {d.price:.0f}")
        print(f"    Andata:  {d.out_dep} -> {d.out_arr}  {d.out_airline} {d.out_flight}  ({oh}, {ostop})")
        print(f"    Ritorno: {d.ret_dep} -> {d.ret_arr}  {d.ret_airline} {d.ret_flight}  ({rh}, {rstop})")


if __name__ == "__main__":
    main()
