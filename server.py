#!/usr/bin/env python

from concurrent import futures
import time
import grpc
import logging
import os
from kiner.producer import KinesisProducer
from google.protobuf.json_format import MessageToDict

from buda.services.events_collector_service_pb2 import Response
import buda.services.events_collector_service_pb2_grpc as collector_grpc
from grpc_health.v1 import health_pb2
from grpc_health.v1 import health_pb2_grpc

logging.basicConfig()

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class EventsCollectorServicer(collector_grpc.EventsCollectorServicer):
    def __init__(self):
        self.producers = {}

        self.add_producer("funnel_events")
        self.add_producer("funnels")
        self.add_producer("subscription_created")
        self.add_producer("subscription_period_updated")
        self.add_producer("subscription_cancelled")
        self.add_producer("visits")
        self.add_producer("signups")
        self.add_producer("signins")
        self.add_producer("actions_taken")

    def Check(self, request, context):
        SERVING_STATUS = health_pb2.HealthCheckResponse.SERVING
        return health_pb2.HealthCheckResponse(status=SERVING_STATUS)

    def add_producer(self, name, **args):
        producer = KinesisProducer("buda_{}".format(name), **args)
        self.producers[name] = producer

        logger.info("Added producer {}".format(name))

        return producer

    def send(self, name, message):
        if message.HasField("id"):
            logger.info("Collecting {} : {}".format(name, message.id))
        else:
            logger.warning(
                "Expecting message for stream {} to have an id field!".format(name)
            )

        data = message.SerializeToString()
        message_json = MessageToDict(message)

        if os.getenv("ENV", "prod") == "dev":
            logger.info(data)

        self.producers[name].put_record(data)

    def CollectFunnelEvent(self, funnel_event, context):
        self.send("funnel_events", funnel_event)
        return Response(message="OK")

    def CollectFunnel(self, funnel, context):
        self.send("funnels", funnel)
        return Response(message="OK")

    def CollectSubscriptionCreated(self, subscription_created, context):
        self.send("subscription_created", subscription_created)
        return Response(message="OK")

    def CollectSubscriptionPeriodUpdated(self, subscription_period_updated, context):
        self.send("subscription_period_updated", subscription_period_updated)
        return Response(message="OK")

    def CollectSubscriptionCancelled(self, subscription_cancelled, context):
        self.send("subscription_cancelled", subscription_cancelled)
        return Response(message="OK")

    def CollectVisit(self, visit, context):
        self.send("visits", visit)
        return Response(message="OK")

    def CollectSignup(self, signup, context):
        self.send("signups", signup)
        return Response(message="OK")

    def CollectSignin(self, signin, context):
        self.send("signins", signin)
        return Response(message="OK")

    def CollectActionTaken(self, action_taken, context):
        self.send("actions_taken", action_taken)
        return Response(message="OK")


if __name__ == "__main__":
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    logger.info("Server initialized")

    service = EventsCollectorServicer()

    collector_grpc.add_EventsCollectorServicer_to_server(service, server)
    health_pb2_grpc.add_HealthServicer_to_server(service, server)

    logger.info("Servicer added")

    server.add_insecure_port("[::]:50051")
    server.start()
    logger.info("Server started")

    try:
        while True:
            time.sleep(10000)
    except KeyboardInterrupt:
        server.stop(0)

