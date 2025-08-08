# import asyncio
# from config import settings


# from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

# from db.repo import get_last_gassensors


# engine = create_async_engine(settings.sqlite_async_dsn, echo=False)


# async def main():
#     async with AsyncSession(engine) as session:
#         sensors = await get_last_gassensors(session)
#         print(sensors)


# if __name__ == "__main__":
#     asyncio.run(main())


from config import GS_PROBE, GS_PUMP, GasRooms


paths = [f"/images/{i}.png" for i in GasRooms]

points = dict(
    zip(
        GS_PUMP + GS_PROBE,
        [(550, 280), (930, 280), (60, 530), (930, 1170), (630, 290), (160, 700)],
    )
)

[print(type(i)) for i in paths]
print(paths)
print(points)
