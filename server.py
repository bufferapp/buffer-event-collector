#!/usr/bin/env python

from concurrent import futures
import time
import grpc
import logging
from kiner.producer import KinesisProducer
import signal
import os

from buda.services.events_collector_service_pb2 import Response
import buda.services.events_collector_service_pb2_grpc as collector_grpc
logging.basicConfig()

logger = logging.getLogger()
logger.setLevel(logging.INFO)

_ONE_DAY_IN_SECONDS = 60 * 60 * 24


class EventsCollectorServicer(collector_grpc.EventsCollectorServicer):

    def __init__(self):
        self.producers = {}

        self.add_producer('funnel_events')
        self.add_producer('funnels')
        self.add_producer('subscription_created')
        self.add_producer('subscription_period_updated')
        self.add_producer('subscription_cancelled')
        self.add_producer('visits')
        self.add_producer('signups')
        self.add_producer('signins')
        self.add_producer('actions_taken')


    def add_producer(self, name, **args):
        producer = KinesisProducer('buda_{}'.format(name), **args)
        self.producers[name] = producer

        logger.info('Added producer {}'.format(name))

        return producer

    def send(self, name, message):
        if message.HasField('id'):
            logger.info('Collecting {} : {}'.format(name, message.id))
        else:
            logger.warning(
                'Expecting message for stream {} to have an id field!'
                .format(name))

        data = message.SerializeToString()
        if os.getenv('ENV', 'prod') == 'dev':
            logger.info(data)
        self.producers[name].put_record(data)

    def CollectFunnelEvent(self, funnel_event, context):
        self.send('funnel_events', funnel_event)
        return Response(message='OK')

    def CollectFunnel(self, funnel, context):
        self.send('funnels', funnel)
        return Response(message='OK')

    def CollectSubscriptionCreated(self, subscription_created, context):
        self.send('subscription_created', subscription_created)
        return Response(message='OK')

    def CollectSubscriptionPeriodUpdated(self,
                                         subscription_period_updated, context):
        self.send('subscription_period_updated', subscription_period_updated)
        return Response(message='OK')

    def CollectSubscriptionCancelled(self, subscription_cancelled, context):
        self.send('subscription_cancelled', subscription_cancelled)
        return Response(message='OK')

    def CollectVisit(self, visit, context):
        self.send('visits', visit)
        return Response(message='OK')

    def CollectSignup(self, signup, context):
        self.send('signups', signup)
        return Response(message='OK')

    def CollectSignin(self, signin, context):
        self.send('signins', signin)
        return Response(message='OK')

    def CollectActionTaken(self, action_taken, context):
        self.send('actions_taken', action_taken)
        return Response(message='OK')


not_interupted = True


def handler_stop_signals(signum, frame):
    global not_interupted
    not_interupted = False


if __name__ == '__main__':
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    logger.info('Server initialized')

    collector_grpc.add_EventsCollectorServicer_to_server(
        EventsCollectorServicer(),
        server
    )
    logger.info('Servicer added')

    server.add_insecure_port('[::]:50051')
    server.start()
    logger.info('Server started')

    signal.signal(signal.SIGINT, handler_stop_signals)
    signal.signal(signal.SIGTERM, handler_stop_signals)

    while not_interupted:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            server.stop(0)
    server.stop(0)
