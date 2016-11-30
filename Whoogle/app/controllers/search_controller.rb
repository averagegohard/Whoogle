class SearchController < ApplicationController
  def concepts
  	# assign the :handle variable that was passed in from the homepage view to @handle
  	# this is so we can access it in the next view
    @handle = params[:handle]
    # use the helper function getConcepts (which is located in /app/helpers/search_helper.rb)
    # in order to make the API call and get the data the way we want it
    @concepts = view_context.getConcepts(params[:handle])
  end
  # once the controller is done with the functions that it was assigned to do, it will generate the
  # html page located in /app/views/search/concepts.html.erb and display that to the client
end
