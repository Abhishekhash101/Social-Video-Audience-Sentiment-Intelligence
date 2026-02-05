YOUTUBE_API='AIzaSyBS57fQDroS9l3BfOOSjaZsntkb7h-6FAI'


from googleapiclient.discovery import build

youtube=build('youtube','v3',developerKey=YOUTUBE_API)

request=youtube.channels().list(
    part='statistics',
    forUsername='schafer5'
)


response=request.execute()

print(response)