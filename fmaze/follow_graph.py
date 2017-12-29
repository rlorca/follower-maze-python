class FollowNetwork:

    def __init__(self):
        self.followMap = {}

    def follow(self, followerId, followeeId):


        if followeeId not in self.followMap:
            self.followMap[followeeId] = set()

        self.followMap[followeeId].add(followerId)

    def unfollow(self, followerId, followeeId):
        return followeeId in self.followMap and \
               self.followMap[followeeId].discard(followerId)

    def followers(self, followeeId):
        return self.followMap.get(followeeId, set())