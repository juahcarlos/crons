import asyncio
import json
import time

from grpclib.client import Channel
from db.grpc_lib import TestStub

from sqlalchemy import delete, insert, select, update, VARCHAR
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.dialects import mysql
from sqlalchemy.sql import text

from config import settings
from lib.logs import log


async def request(data):
    print("request", "settings", settings.GRPC_PORT)
    async with Channel(host=settings.GRPC_HOST, port=settings.GRPC_PORT) as channel:
        stub = TestStub(channel)
        response = await stub.test(test=data)
        return response.test_res


class DbMain:
    def __init__(self) -> None:
        self.engine_ = create_async_engine(
            "mysql+aiomysql://",
        )
        self.data_class = None

    def sql_text_(self, statement) -> str:
        compiled = statement.compile(dialect=mysql.dialect(), compile_kwargs={"literal_binds": True})
        try:
            text = str(compiled) % compiled.params
            return text
        except Exception as ex:
            print("ex", ex)

    async def query(self, statement):
        query_ = self.sql_text_(statement)
        print(f"query_ {query_}")
        return await request(query_)

    async def result(self, statement):
        # print(f"database result statement \n {statement}")
        res = await self.query(statement)
        # print(f"database result res \n {res}")
        return await self.result_list(res)

    async def result_insert(self, statement):
        # print(f"database result_insert statement \n {statement}")
        res = await self.query(statement)
        return res
        # return await self.result_list(res)

    async def result_list(self, statement):
        res = await self.query(statement)
        res_list = json.loads(res)
        result_ = []
        # log.debug(f"database result_list res \n {res_list}")
        if len(res_list) > 0:
            for row in res_list:
                try:
                    result_.append(self.data_class(**row))
                except Exception as ex:
                    log.error(f"db_main DbMain result_list loop ERROR ex {ex}")
            # log.debug(f"database result_list result_ \n {result_}")
        return result_        

    async def result_one(self, statement):
        result_list = await self.result_list(statement)
        if len(result_list) > 0:
            return result_list[0]

