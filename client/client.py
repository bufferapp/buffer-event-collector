import grpc
import uuid
import time

from entities.funnel_pb2 import FunnelEvent
import services.event_collector_pb2_grpc as collector_grpc


if __name__ == '__main__':
    channel = grpc.insecure_channel('100.96.1.147:50051')
    stub = collector_grpc.EventCollectorStub(channel)

    for i in range(1000):

        v = FunnelEvent(
            id='id_{}'.format(uuid.uuid4().hex[:10]),
            user_id='user_id_{}'.format(uuid.uuid4().hex[:10]),
            funnel_id='funnel_id_{}'.format(uuid.uuid4().hex[:10]),
            funnel_event_id='funnel_event_id_{}'.format(uuid.uuid4().hex[:10])
        )

        v.created_at.GetCurrentTime()

        stub.TrackFunnelEvent(v)
        time.sleep(0.1)
