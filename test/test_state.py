
from unittest import TestCase

from fmaze.state import FollowNetwork

class TestFollowNetwork(TestCase):

    def setUp(self):
        self.state = FollowNetwork()

    def test_follow_cycle(self):

        self.state.follow("alice", "bob")

        # add one follower
        self.assertIn("alice", self.state.followers("bob"), "New follower ")

        # add another follower
        self.state.follow("charlie", "bob")
        self.assertIn("charlie", self.state.followers("bob"), "New follower ")

        # remove new follower
        self.state.unfollow("charlie", "bob")

        # second follower is not in the set anymore
        self.assertNotIn("charlie", self.state.followers("bob"), "New follower ")

        # initial follower should be there
        self.assertIn("alice", self.state.followers("bob"), "New follower ")

    def test_unfollow_unknown_followee(self):
        self.assertFalse(self.state.unfollow("not bob", "not alice"))

    def test_unfollow_unknown_follower(self):
        self.state.follow("alice", "bob")
        self.assertFalse(self.state.unfollow("bob", "charlie"), "Unknown follower")
