from mta_api.feed_parser import FeedParser


def test_feed_parser_mta():
    mta_feed = FeedParser().get_mta_feed()
    assert type(mta_feed) == list

def test_feed_parser_ferry():
    ferry_feed = FeedParser().get_ferry_feed()
    assert type(ferry_feed) == list