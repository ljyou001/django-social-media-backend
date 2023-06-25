class TweetPhotoStatus:
    """
    All status you can have for the tweet photo's status

    Using the full capitalization words below means it is a constant
    All the contants are defined in TweetPhotoStatus class, which means
    they are a series of constants of TweetPhotoStatus class
    """
    PENDING = 0
    APPROVED = 1
    REJECTED = 2

TWEET_PHOTO_STATUS_CHOICES = (
    (TweetPhotoStatus.PENDING, 'Pending'),
    (TweetPhotoStatus.APPROVED, 'Approved'),
    (TweetPhotoStatus.REJECTED, 'Rejected'),
)
# touple of touple
# First level touple means the choices you can make
# Second level touple means (value of this choice, information in admin panel) 