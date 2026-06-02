"""AgentVoli — weekend scan: cerca voli short-haul dall'Italia per il prossimo weekend.

Outbound: prossimo sabato (calcolato a runtime, partendo da domani)
Return:   domenica dopo (preferibilmente sera)
Vincolo:  durata volo a tratta <= 3h
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

# Prossimo sabato a partire da domani (se oggi è sabato, salta al weekend successivo).
_TOMORROW = date.today() + timedelta(days=1)
_SAT = _TOMORROW + timedelta(days=(5 - _TOMORROW.weekday()) % 7)
OUTBOUND_DATE = _SAT.isoformat()
RETURN_DATE = (_SAT + timedelta(days=1)).isoformat()
MAX_LEG_MINUTES = 180
RETURN_AFTER_HOUR = 17

ORIGINS = [Airport.PSA, Airport.FLR, Airport.BLQ]
DESTINATIONS = [
    Airport.BCN, Airport.MAD, Airport.LIS, Airport.CDG, Airport.AMS,
    Airport.BRU, Airport.LHR, Airport.BER, Airport.MUC, Airport.VIE,
    Airport.ZRH, Airport.PRG, Airport.BUD, Airport.ATH,
]


@dataclass
class Deal:
    origin: str
    destination: str
    price: float
    out_dep: str
    out_arr: str
    out_airline: str
    out_flight: str
    out_minutes: int
    ret_dep: str
    ret_arr: str
    ret_airline: str
    ret_flight: str
    ret_minutes: int
    ret_stops: int
    out_stops: int


def search_pair(origin: Airport, destination: Airport) -> list[Deal]:
    filters = FlightSearchFilters(
        trip_type=TripType.ROUND_TRIP,
        passenger_info=PassengerInfo(adults=1),
        seat_type=SeatType.ECONOMY,
        stops=MaxStops.NON_STOP,
        sort_by=SortBy.CHEAPEST,
        flight_segments=[
            FlightSegment(
                departure_airport=[[origin, 0]],
                arrival_airport=[[destination, 0]],
                travel_date=OUTBOUND_DATE,
            ),
            FlightSegment(
                departure_airport=[[destination, 0]],
                arrival_airport=[[origin, 0]],
                travel_date=RETURN_DATE,
            ),
        ],
    )

    deals: list[Deal] = []
    try:
        results = SearchFlights().search(filters) or []
    except Exception as e:
        print(f"  [skip] {origin.name}->{destination.name}: {type(e).__name__}: {e}")
        return deals

    for outbound, ret in results:
        if outbound.duration > MAX_LEG_MINUTES or ret.duration > MAX_LEG_MINUTES:
            continue
        ret_first_dep = ret.legs[0].departure_datetime
        if ret_first_dep.hour < RETURN_AFTER_HOUR:
            continue
        out_leg_first = outbound.legs[0]
        out_leg_last = outbound.legs[-1]
        ret_leg_first = ret.legs[0]
        ret_leg_last = ret.legs[-1]
        deals.append(Deal(
            origin=origin.name,
            destination=destination.name,
            price=float(outbound.price),
            out_dep=out_leg_first.departure_datetime.strftime("%a %d-%b %H:%M"),
            out_arr=out_leg_last.arrival_datetime.strftime("%H:%M"),
            out_airline=out_leg_first.airline.name,
            out_flight=str(out_leg_first.flight_number),
            out_minutes=outbound.duration,
            out_stops=outbound.stops,
            ret_dep=ret_leg_first.departure_datetime.strftime("%a %d-%b %H:%M"),
            ret_arr=ret_leg_last.arrival_datetime.strftime("%H:%M"),
            ret_airline=ret_leg_first.airline.name,
            ret_flight=str(ret_leg_first.flight_number),
            ret_minutes=ret.duration,
            ret_stops=ret.stops,
        ))
    return deals


def main():
    pairs = [(o, d) for o in ORIGINS for d in DESTINATIONS]
    print(f"Scansione di {len(pairs)} rotte (sabato {OUTBOUND_DATE} -> domenica {RETURN_DATE})...")
    print(f"Vincoli: non-stop, durata <= {MAX_LEG_MINUTES//60}h, ritorno dopo le {RETURN_AFTER_HOUR}:00\n")

    all_deals: list[Deal] = []
    with ThreadPoolExecutor(max_workers=8) as ex:
        futures = {ex.submit(search_pair, o, d): (o, d) for o, d in pairs}
        for fut in as_completed(futures):
            o, d = futures[fut]
            try:
                deals = fut.result()
                if deals:
                    cheapest = min(deals, key=lambda x: x.price)
                    print(f"  {o.name} -> {d.name}: {len(deals)} opzioni, min EUR {cheapest.price:.0f}")
                else:
                    print(f"  {o.name} -> {d.name}: nessuna opzione (filtri)")
                all_deals.extend(deals)
            except Exception as e:
                print(f"  [error] {o.name}->{d.name}: {e}")

    if not all_deals:
        print("\nNessuna offerta trovata.")
        return

    all_deals.sort(key=lambda x: x.price)

    print("\n" + "=" * 80)
    print(f"TOP 15 OFFERTE WEEKEND {OUTBOUND_DATE} -> {RETURN_DATE}")
    print("=" * 80)
    for i, d in enumerate(all_deals[:15], 1):
        print(
            f"\n{i:2d}. {d.origin} -> {d.destination}  EUR {d.price:.0f}  "
            f"({d.out_minutes//60}h{d.out_minutes%60:02d}m / {d.ret_minutes//60}h{d.ret_minutes%60:02d}m)"
        )
        print(
            f"    Andata:  {d.out_dep} -> {d.out_arr}  "
            f"{d.out_airline} {d.out_flight}"
        )
        print(
            f"    Ritorno: {d.ret_dep} -> {d.ret_arr}  "
            f"{d.ret_airline} {d.ret_flight}"
        )


if __name__ == "__main__":
    main()
