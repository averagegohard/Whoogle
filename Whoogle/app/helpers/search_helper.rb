module SearchHelper
	require 'httparty'
	def getConcepts(handle)
		key = "VKuS1JkgnomshHxfv1Yu8AIS6tzGp1aUztsjsnorGKylwIxnMQ"
        accept = 'application/json'
        @options = {'X-Mashape-Key' => key, 'Accept' => accept}
        response = HTTParty.get('https://alchemy.p.mashape.com/url/URLGetRankedConcepts?baseUrl=<required>&linkedData=false&maxRetrieve=24&outputMode=json&url=https%3A%2F%2Ftwitter.com%2F'+handle+'/with_replies', :headers => @options)
		return response['concepts']
	end
end
