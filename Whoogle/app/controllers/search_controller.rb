class SearchController < ApplicationController
  def concepts
    @handle = params[:handle]
    @concepts = view_context.getConcepts(params[:handle])
  end
end
