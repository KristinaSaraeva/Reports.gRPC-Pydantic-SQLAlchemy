#!/usr/bin/env python3
import argparse
import grpc
import reporting_pb2
import reporting_pb2_grpc
from google.protobuf.json_format import MessageToDict
from pydantic import BaseModel, ValidationError, field_validator, Field
from typing import Optional
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, JSON, ForeignKey, UniqueConstraint
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.exc import IntegrityError
import json



engine = create_engine('postgresql://postgres:password123@localhost/postgres')

Base = declarative_base()

class Spaceship(Base):
    __tablename__ = 'spaceships'

    id = Column(Integer, primary_key=True)
    alignment = Column(String)
    name = Column(String)
    ship_class = Column(String)
    length = Column(Float)
    crew_size = Column(Integer)
    is_armed = Column(Boolean)
    officers = Column(JSONB)

    __table_args__ = (
        UniqueConstraint('name', 'officers', name='unique_name_officers'),
    )

class Officer(Base):
    __tablename__ = 'officers'

    id = Column(Integer, primary_key=True)
    officer = Column(String)
    alignment = Column(String)
    spaceship_id = Column(Integer, ForeignKey('spaceships.id'))
    spaceship = relationship("Spaceship")

Base.metadata.schema = "public"
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()


class SpaceshipModel(BaseModel):
    alignment: str
    name: str
    ship_class: str = Field(alias="shipClass")
    length: float = Field(ge=80, le=20000)
    crew_size: int = Field(ge=4, le=500, alias="crewSize")
    is_armed: bool = Field(alias="isArmed")
    officers: Optional[list]

    @field_validator('name')
    @classmethod
    def check_name(cls, v, values):
        if v == "Unknown" and getattr(values, 'alignment', None) == "ALLY":
            raise ValueError("Ship name cannot be 'Unknown'")
        return v

    @field_validator('officers')
    @classmethod
    def check_name(cls, v, values):
        if len(v) < 1 and getattr(values, 'alignment', None) == "ALLY":
            raise ValueError("Ship has to have at least one officer")
        return v

    @field_validator('ship_class')
    @classmethod
    def check_ship_class(cls, v, values):
        class_ranges = {
            'CORVETTE': (80, 250),
            'FRIGATE': (300, 600),
            'CRUISER': (500, 1000),
            'DESTROYER': (800, 2000),
            'CARRIER': (1000, 4000),
            'DREADNOUGHT': (5000, 20000)
        }

        if v not in class_ranges:
            raise ValueError("Invalid ship class")

        length_range = class_ranges[v]
        length = getattr(values, 'length', None)
        if length is not None and not (length_range[0] <= length <= length_range[1]):
            raise ValueError(f"Invalid length for {v}")

        crew_size_range = {
            'CORVETTE': (4, 10),
            'FRIGATE': (10, 15),
            'CRUISER': (15, 30),
            'DESTROYER': (50, 80),
            'CARRIER': (120, 250),
            'DREADNOUGHT': (300, 500)
        }
        crew_size = getattr(values, 'crew_size', None)
        if crew_size is not None and not (crew_size_range[v][0] <= crew_size <= crew_size_range[v][1]):
            raise ValueError(f"Invalid crew size for {v}")

        if v == "CARRIER" and getattr(values,'is_armed', None):
            raise ValueError("Carriers cannot be armed")

        if v == "FRIGATE" and getattr(values,'alignment', None) == "ENEMY":
            raise ValueError("Frigates cannot be enemies")
        
        if v == "DESTROYER" and getattr(values,'alignment', None) == "ENEMY":
            raise ValueError("Destroyers cannot be enemies")

        return v
        


def run(longitude, latitude, distance):
    channel = grpc.insecure_channel('localhost:50051') 
    stub = reporting_pb2_grpc.ReportingStub(channel)
    coordinates = reporting_pb2.EclipticCoordinates(
            longitude=longitude,
            latitude=latitude,
            distance=distance
    )

    response = stub.GetSpaceshipStream(coordinates)
    for spaceship in response:
        spaceship_dict = MessageToDict(spaceship)
        try:
            spaceship_model = SpaceshipModel.model_validate(spaceship_dict)
  
            new_spaceship = Spaceship(
                alignment=spaceship_model.alignment,
                name=spaceship_model.name,
                ship_class=spaceship_model.ship_class,
                length=spaceship_model.length,
                crew_size=spaceship_model.crew_size,
                is_armed=spaceship_model.is_armed,
                officers=spaceship_model.officers
            )
            try:
                session.add(new_spaceship)
                session.commit()
                if len(new_spaceship.officers) > 0:
                    for officer in new_spaceship.officers:
                        new_officer = Officer(
                            officer=officer["firstName"] + " " + officer["lastName"] + ", " + officer["rank"],
                            alignment=new_spaceship.alignment,
                            spaceship_id=new_spaceship.id
                        )
                        session.add(new_officer)
                        session.commit()
            except IntegrityError as e:
                session.rollback()
            
            
        except ValidationError as e:    
            pass
        else:
            print(spaceship_model.model_dump_json(indent=2))


def list_traitors():
    traitors = (
        session.query(Officer.officer)
        .join(Spaceship, Officer.spaceship_id == Spaceship.id)
        .filter(Spaceship.alignment == "ALLY")
        .filter(Officer.officer.in_(
            session.query(Officer.officer)
            .join(Spaceship, Officer.spaceship_id == Spaceship.id)
            .filter(Spaceship.alignment == "ENEMY")
        ))
        .all()
    )

    traitors_list = [{"officer": traitor[0]} for traitor in traitors]
    traitors_json = json.dumps(traitors_list, indent=2)
    print(traitors_json)


def create_ship(ali, n):
    new_spaceship = Spaceship(
        alignment=ali,
        name=n,
        ship_class="CRUISER",
        length=900.5,
        crew_size=20,
        is_armed=True,
        officers=[{"firstName": "James", "lastName": "Kirk", "rank": "Captain"},
                  {"firstName": "Jean-Luc", "lastName": "Picard", "rank": "Commander"},
                  {"firstName": "Benjamin", "lastName": "Sisko", "rank": "Lieutenant Commander"},
                  {"firstName": "Kathryn", "lastName": "Janeway", "rank": "Lieutenant"},
                  {"firstName": "Jonathan", "lastName": "Archer", "rank": "Lieutenant"}]

    )
    try:
        session.add(new_spaceship)
        session.commit()
        if len(new_spaceship.officers) > 0:
            for officer in new_spaceship.officers:
                new_officer = Officer(
                    officer=officer["firstName"] + " " + officer["lastName"] + ", " + officer["rank"],
                    alignment=new_spaceship.alignment,
                    spaceship_id=new_spaceship.id
                )
                session.add(new_officer)
                session.commit()
    except IntegrityError as e:
        session.rollback()



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run reporting client with longitude, latitude, and distance')
    parser.add_argument('action', choices=['scan', 'traitors', 'create_traitors'], help='Action to perform')
    parser.add_argument('coordinates', nargs='*', type=float, help='Coordinates for scanning')
    args = parser.parse_args()

    if args.action == 'scan':
        if len(args.coordinates) == 3:
            run(*args.coordinates)
        else:
            print("Error: Please provide 3 coordinates for scanning")

    elif args.action == 'traitors':
         list_traitors()

    elif args.action == 'create_traitors':
        create_ship("ENEMY", "Millennium Falcon")
        create_ship("ALLY", "X-Wing")
    
