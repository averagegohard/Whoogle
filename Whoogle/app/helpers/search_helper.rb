module SearchHelper
	# use the module HTTParty to access the web in Ruby
	require 'httparty'

	def getConcepts(handle)
		"""
		Input: A Twitter handle (either with or w/o the @ sign)
		Output: The 'concepts' that they talk about the most
		"""
		# our api options and details
		key = "VKuS1JkgnomshHxfv1Yu8AIS6tzGp1aUztsjsnorGKylwIxnMQ"
        accept = 'application/json'
        @options = {'X-Mashape-Key' => key, 'Accept' => accept}
        # the actual response
        # TODO make this go to every tweet the user has made
        response = HTTParty.get('https://alchemy.p.mashape.com/url/URLGetRankedConcepts?baseUrl=<required>&linkedData=false&maxRetrieve=24&-outputMode=json&url=https%3A%2F%2Ftwitter.com%2F'+handle+'/with_replies', :headers => @options)

        # if the response is 'OK' we can return the data
        if response['results']['status'] == 'OK'
			return response['results']['concepts']
		# otherwise something went wrong
		else
			# display an error message
			return 'Cannot connect to AlchemyAPI, try again later...'
		end
	end

	# method stub to getSentiments from the concepts
	def getSentiments(concepts)
		"""
		Input: A list of 'concepts' a Twitter user talks about the most.
		Output: A list of how a person feels about each of these 'concepts'
		"""

		# add each concept to something
		concepts.each{
		}
	end
end
