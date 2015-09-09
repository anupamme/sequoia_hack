import endpoints

class Hotel(messages.Message):
    hotel_id = messages.IntegerField(1)
    name = messages.StringField(2)
    attribute = messages.StringField(3)
    cover_image = messages.StringField(4)
    images = messages.StringField(5, repeated=True)
    reviews = messages.StringField(6, repeated=True)
    address = messages.StringField(7, repeated=True)

class HotelCollection(messages.Message):
    items = messages.MessageField(Hotel, 1, repeated=True)

@endpoints.api(name='helloworld', version='v1')
class HelloWorldApi(remote.Service):
    
    MULTIPLY_METHOD_RESOURCE = endpoints.ResourceContainer(
            search_string = messages.StringField(1, required=True))
    
    @endpoints.method(MULTIPLY_METHOD_RESOURCE, HotelCollection,
                      path='hellogreeting', http_method='GET',
                      name='greetings.listGreeting')
    def greetings_list(self, request):
        print 'I am in api call: ' + locationKey
        #locationKey = request.destination
        raise ValueError('A very specific bad thing happened')
        return {"val": "I work!"}
    

APPLICATION = endpoints.api_server([HelloWorldApi])