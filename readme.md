# TRAITORS

A Python project which has gRPC is a client-server communication framework. The server provides a response-streaming
endpoint, where it receives a set of coordinates(see below), and responds with a stream of Spaceships.
Every spaceship has several characteristics:

- Alignment (Ally/Enemy)
- Name (can be 'Unknown' for enemy ships)
- Class, which is one of {Corvette, Frigate, Cruiser, Destroyer, Carrier, Dreadnought}
- Length in meters
- Size of the crew
- Whether or not the ship is armed
- One or more officers responsible for the ship(if it is an ally ship, enemy ships can be without any officers)  

All the Spaceships are randomly generated and checked if they fit certain parameters with Pydantic.

| Class       | Length     | Crew    | Can be armed? | Can be hostile? |
|-------------|------------|---------|---------------|-----------------|
| Corvette    | 80-250     | 4-10    | Yes           | Yes             |
| Frigate     | 300-600    | 10-15   | Yes           | No              |
| Cruiser     | 500-1000   | 15-30   | Yes           | Yes             |
| Destroyer   | 800-2000   | 50-80   | Yes           | No              |
| Carrier     | 1000-4000  | 120-250 | No            | Yes             |
| Dreadnought | 5000-20000 | 300-500 | Yes           | Yes             |

All the Spaceship info is stored in Postgres database.  
If you you encounter the same officers both on _enemy_ and _ally_ ships they are regarded as traitors.

### Dependencies

- Python3
- Postgress

### Installing

1. Clone this repository to your local machine.
2. Create the environment and activate it.
3. Before you install the requirements run  
 `pip3 install --upgrade pip`  
 `pip3 install --upgrade setuptools` and only then  
 `pip3 install --no-cache-dir -r requirements.txt`  
4. Then run `make proto` to compile python modules from the proto file.
5. Turn on the database.
6. Being in one terminak run `make server`.
7. Open another terminal window.
 Run `./report.py scan 'longitude' 'latitude' 'distance'` (actually can be any random numbers, see the section below) to see the list of Spaceships in that area.
 Run `./report.py traitors` to get the list of traitors.
 Actually, the chance to randomly create identical 'twins' on different ships is really tiny.  
 So I have made a hardcode function that creates five traitors. Run `./report.py create_traitors` and then check for them.




### _The geocentric ecliptic coordinate system is used_

Longitude: +90 (north ecliptic pole) -90 (south ecliptic pole)
Latitude: 0-360 (from the vernal equinox point)
Distance in astronomical units (AU)"

1 astronomical unit 	= 149597870700 metres (by definition)

= 149597870.7 kilometres (exactly)

≈ 92955807.2730 miles

≈ 499.004783836 light-seconds

≈ 1.58125074098×10−5 light-years

≈ 4.84813681113×10−6 parsecs

![pic](../ex00/img/470px-Earths_orbit_and_ecliptic.png)

## Author

[Kristina Saraeva](https://github.com/KristinaSaraeva)

© 2024 KristinaSaraeva