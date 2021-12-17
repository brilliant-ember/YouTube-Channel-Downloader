class VideoExistsError(Exception):
# a custom exception if the video file already exists
     pass

class NeedToScrollToGetVideos(Exception):
    def __init__(self, videos_so_far:dict, message="" ):
        super().__init__(message)
        self.videos_so_far = videos_so_far
    